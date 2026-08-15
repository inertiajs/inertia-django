import logging
from functools import wraps
from http import HTTPStatus
from json import dumps as json_encode
from typing import Any, Callable

from django.contrib.messages import get_messages
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.cache import patch_vary_headers

from .prop_classes import (
    AlwaysProp,
    CallableProp,
    DeferredProp,
    IgnoreOnFirstLoadProp,
    MergeableProp,
    ScrollProp,
)
from .settings import settings

try:
    # Must be early-imported so tests can patch it with
    # a mock module
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

INERTIA_REQUEST_ENCRYPT_HISTORY = "_inertia_encrypt_history"
INERTIA_SESSION_CLEAR_HISTORY = "_inertia_clear_history"
INERTIA_SESSION_PRESERVE_FRAGMENT = "_inertia_preserve_fragment"

INERTIA_TEMPLATE = "inertia.html"
INERTIA_SSR_TEMPLATE = "inertia_ssr.html"
SKIP_PROP = object()


class InertiaRequest(HttpRequest):
    def __init__(self, request: HttpRequest):
        super().__init__()
        self.__dict__.update(request.__dict__)

    @property
    def inertia(self) -> dict[str, Any]:
        inertia_attr = self.__dict__.get("inertia")
        return (
            inertia_attr.all() if inertia_attr and hasattr(inertia_attr, "all") else {}
        )

    @property
    def shared_keys(self) -> list[str]:
        inertia_attr = self.__dict__.get("inertia")
        return (
            inertia_attr.keys()
            if inertia_attr and hasattr(inertia_attr, "keys")
            else []
        )

    def is_a_partial_render(self, component: str) -> bool:
        return self.headers.get("X-Inertia-Partial-Component", "") == component

    def header_list(self, name: str) -> list[str] | None:
        if name not in self.headers:
            return None
        return [
            value.strip() for value in self.headers[name].split(",") if value.strip()
        ]

    def partial_keys(self) -> list[str] | None:
        return self.header_list("X-Inertia-Partial-Data")

    def partial_except_keys(self) -> list[str] | None:
        return self.header_list("X-Inertia-Partial-Except")

    def reset_keys(self) -> list[str]:
        return self.header_list("X-Inertia-Reset") or []

    def except_once_prop_keys(self) -> list[str]:
        """
        Return the list of once prop keys that the client reports as already
        loaded, sourced from the X-Inertia-Except-Once-Props request header.
        """
        return self.header_list("X-Inertia-Except-Once-Props") or []

    def infinite_scroll_merge_intent(self) -> str:
        """
        Return the merge intent for infinite scroll requests.

        The X-Inertia-Infinite-Scroll-Merge-Intent header is set by the client
        to indicate whether merge-able props in this partial reload should be
        appended to or prepended before existing client-side data.  Returns
        "append" when the header is absent.
        """
        return self.headers.get("X-Inertia-Infinite-Scroll-Merge-Intent", "append")

    def is_inertia(self) -> bool:
        return "X-Inertia" in self.headers

    def should_encrypt_history(self) -> bool:
        should_encrypt = getattr(
            self, INERTIA_REQUEST_ENCRYPT_HISTORY, settings.INERTIA_ENCRYPT_HISTORY
        )
        if not isinstance(should_encrypt, bool):
            raise TypeError(
                f"Expected bool for encrypt_history, got {type(should_encrypt).__name__}"
            )
        return should_encrypt


class PropsResolver:
    """Resolve props once and collect Inertia v3 metadata by dotted path."""

    def __init__(self, request: InertiaRequest, component: str, props: dict[str, Any]):
        self.request = request
        self.component = component
        self.props = props
        self.metadata: dict[str, Any] = {
            "deferredProps": {},
            "mergeProps": [],
            "prependProps": [],
            "deepMergeProps": [],
            "matchPropsOn": [],
            "scrollProps": {},
            "onceProps": {},
            "rescuedProps": [],
        }

    def resolve(self) -> tuple[dict[str, Any], dict[str, Any]]:
        resolved = self._resolve_mapping(self.props)
        return resolved, {key: value for key, value in self.metadata.items() if value}

    def _resolve_mapping(
        self, props: dict[str, Any], prefix: str = "", parent_resolved: bool = False
    ) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for key, prop in props.items():
            path = f"{prefix}.{key}" if prefix else key
            value = self._resolve_prop(prop, path, parent_resolved)
            if value is not SKIP_PROP:
                resolved[key] = value
        return resolved

    def _resolve_prop(self, prop: Any, path: str, parent_resolved: bool = False) -> Any:
        if (
            not parent_resolved
            and not isinstance(prop, AlwaysProp)
            and self._excluded_by_partial_request(path)
        ):
            return SKIP_PROP

        if isinstance(prop, dict):
            if not prop:
                return {}
            resolved = self._resolve_mapping(prop, path, parent_resolved)
            return resolved if resolved else SKIP_PROP
        if isinstance(prop, list):
            return self._resolve_list(prop, path, parent_resolved)

        is_cached_once_prop = self._should_skip_loaded_once_prop(prop, path)
        self._collect_metadata(
            prop,
            path,
            include_deferred=not is_cached_once_prop,
        )
        if is_cached_once_prop:
            return SKIP_PROP
        if not self._is_partial() and (
            isinstance(prop, IgnoreOnFirstLoadProp)
            or isinstance(prop, ScrollProp)
            and prop.defer
        ):
            return SKIP_PROP

        try:
            value = prop() if callable(prop) else prop
        except Exception:
            if isinstance(prop, DeferredProp) and prop.rescue:
                self.metadata["rescuedProps"].append(path)
                return SKIP_PROP
            raise

        if isinstance(value, CallableProp):
            return self._resolve_prop(value, path, parent_resolved=True)
        if isinstance(value, dict):
            if not value:
                return {}
            resolved = self._resolve_mapping(value, path, parent_resolved=True)
            return resolved if resolved else SKIP_PROP
        if isinstance(value, list):
            return self._resolve_list(value, path, parent_resolved=True)
        return value

    def _resolve_list(
        self, values: list[Any], path: str, parent_resolved: bool
    ) -> list[Any]:
        resolved: list[Any] = []
        for index, value in enumerate(values):
            item = self._resolve_list_item(value, path, index, parent_resolved)
            if item is not SKIP_PROP:
                resolved.append(item)
        return resolved

    def _resolve_list_item(
        self, value: Any, path: str, index: int, parent_resolved: bool
    ) -> Any:
        item_path = f"{path}.{index}"
        if isinstance(value, dict):
            return self._resolve_mapping(value, item_path, parent_resolved)
        if isinstance(value, CallableProp):
            return self._resolve_prop(value, item_path, parent_resolved)
        return value() if callable(value) else value

    def _is_partial(self) -> bool:
        return self.request.is_a_partial_render(self.component)

    def _excluded_by_partial_request(self, path: str) -> bool:
        if not self._is_partial():
            return False
        only = self.request.partial_keys()
        if only is not None and not any(self._paths_overlap(path, key) for key in only):
            return True
        except_keys = self.request.partial_except_keys() or []
        return any(path == key or path.startswith(f"{key}.") for key in except_keys)

    @staticmethod
    def _paths_overlap(left: str, right: str) -> bool:
        return (
            left == right
            or left.startswith(f"{right}.")
            or right.startswith(f"{left}.")
        )

    def _should_skip_loaded_once_prop(self, prop: Any, path: str) -> bool:
        return (
            self.request.is_inertia()
            and not self._is_partial()
            and isinstance(prop, CallableProp)
            and prop.should_resolve_once()
            and not prop.should_be_fresh()
            and prop.once_key(path) in self.request.except_once_prop_keys()
        )

    def _collect_metadata(
        self, prop: Any, path: str, *, include_deferred: bool = True
    ) -> None:
        if not isinstance(prop, CallableProp):
            return
        if (
            include_deferred
            and (
                isinstance(prop, DeferredProp)
                or isinstance(prop, ScrollProp)
                and prop.defer
            )
            and not self._is_partial()
        ):
            self.metadata["deferredProps"].setdefault(prop.group, []).append(path)
        if isinstance(prop, MergeableProp) and prop.should_merge():
            self._collect_merge_metadata(prop, path)
        if prop.should_resolve_once():
            self.metadata["onceProps"][prop.once_key(path)] = {
                "prop": path,
                "expiresAt": prop.once_expires_at(),
            }

    def _collect_merge_metadata(self, prop: MergeableProp, path: str) -> None:
        reset = path in self.request.reset_keys()
        if isinstance(prop, ScrollProp):
            self.metadata["scrollProps"][path] = {**prop.metadata, "reset": reset}
        if reset:
            return
        if prop.should_deep_merge():
            self.metadata["deepMergeProps"].append(path)
        else:
            prepend_paths = prop.merge_paths(path, prepend=True)
            append_paths = prop.merge_paths(path)
            if prepend_paths:
                self.metadata["prependProps"].extend(prepend_paths)
            elif (
                self._is_partial()
                and self.request.infinite_scroll_merge_intent() == "prepend"
            ):
                self.metadata["prependProps"].extend(append_paths)
            else:
                self.metadata["mergeProps"].extend(append_paths)
        self.metadata["matchPropsOn"].extend(
            f"{path}.{match}" for match in prop.match_on()
        )


class BaseInertiaResponseMixin:
    request: InertiaRequest
    component: str
    props: dict[str, Any]
    template_data: dict[str, Any]

    def page_data(self) -> dict[str, Any]:
        clear_history = self.request.session.pop(INERTIA_SESSION_CLEAR_HISTORY, False)
        if not isinstance(clear_history, bool):
            raise TypeError(
                f"Expected bool for clear_history, got {type(clear_history).__name__}"
            )

        should_preserve_fragment = self.request.session.pop(
            INERTIA_SESSION_PRESERVE_FRAGMENT, False
        )
        if not isinstance(should_preserve_fragment, bool):
            raise TypeError(
                f"Expected bool for preserve_fragment, got {type(should_preserve_fragment).__name__}"
            )

        resolved_props, metadata = self.resolve_props()
        _page: dict[str, Any] = {
            "component": self.component,
            "props": resolved_props,
            "url": self.request.get_full_path(),
            "version": settings.INERTIA_VERSION,
            "encryptHistory": self.request.should_encrypt_history(),
            "clearHistory": clear_history,
        }

        if should_preserve_fragment:
            _page["preserveFragment"] = True

        if self.request.shared_keys:
            _page["sharedProps"] = self.request.shared_keys
        flash = self.build_flash()
        if flash:
            _page["flash"] = flash
        _page.update(metadata)

        return _page

    def resolve_props(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return PropsResolver(
            self.request,
            self.component,
            {**self.request.inertia, **self.props},
        ).resolve()

    def build_flash(self) -> dict[str, Any]:
        messages = [
            {"level": message.level_tag, "message": str(message)}
            for message in get_messages(self.request)
        ]
        return {"messages": messages} if messages else {}

    def build_first_load(self, data: Any) -> str:
        context, template = self.build_first_load_context_and_template(data)

        try:
            layout = settings.INERTIA_LAYOUT
            if not layout:
                raise AttributeError("INERTIA_LAYOUT is set, but has a falsy value")
        except AttributeError as ae:
            raise ImproperlyConfigured(
                "INERTIA_LAYOUT must be set in your Django settings"
            ) from ae

        return render_to_string(
            template,
            {
                "inertia_layout": layout,
                **context,
            },
            self.request,
            using=None,
        )

    def build_first_load_context_and_template(
        self, data: Any
    ) -> tuple[dict[str, Any], str]:
        if settings.INERTIA_SSR_ENABLED:
            try:
                response = requests.post(
                    f"{settings.INERTIA_SSR_URL}/render",
                    data=data,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return {
                    **response.json(),
                    **self.template_data,
                }, INERTIA_SSR_TEMPLATE
            except Exception:
                logger.exception("SSR render request failed")

        return {
            "page": data,
            **(self.template_data),
        }, INERTIA_TEMPLATE


class InertiaResponse(BaseInertiaResponseMixin, HttpResponse):
    json_encoder = None

    def __init__(
        self,
        request: HttpRequest,
        component: str,
        props: dict[str, Any] | None = None,
        template_data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.request = InertiaRequest(request)
        self.component = component
        self.props = props or {}
        self.template_data = template_data or {}
        _headers = headers or {}

        data = json_encode(
            self.page_data(),
            cls=self.json_encoder or settings.INERTIA_JSON_ENCODER,
        )
        # Page data is embedded in a JSON script tag for Inertia v3 clients.
        # Escape the few characters that could terminate or alter that script.
        data = (
            data.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
        )

        if self.request.is_inertia():
            _headers = {
                **_headers,
                "X-Inertia": "true",
                "Content-Type": "application/json",
            }
            content = data
        else:
            content = self.build_first_load(data)

        if args:
            super().__init__(
                *args,
                headers=_headers,
                **kwargs,
            )
        else:
            super().__init__(
                content=content,
                headers=_headers,
                **kwargs,
            )
        patch_vary_headers(self, ("X-Inertia",))


def render(
    request: HttpRequest,
    component: str,
    props: dict[str, Any] | None = None,
    template_data: dict[str, Any] | None = None,
) -> InertiaResponse:
    return InertiaResponse(request, component, props or {}, template_data or {})


def location(location: str) -> HttpResponse:
    return HttpResponse(
        "",
        status=HTTPStatus.CONFLICT,
        headers={
            "X-Inertia-Location": location,
        },
    )


def encrypt_history(request: HttpRequest, value: bool = True) -> None:
    setattr(request, INERTIA_REQUEST_ENCRYPT_HISTORY, value)


def clear_history(request: HttpRequest) -> None:
    request.session[INERTIA_SESSION_CLEAR_HISTORY] = True


def preserve_fragment(request: HttpRequest) -> None:
    """
    Signal that the URL fragment should be preserved across the next redirect.

    Call this before returning a redirect response from a view.  On the
    subsequent Inertia page response the page object will include
    ``preserveFragment: true``, instructing the client to carry the original
    request's URL fragment to the redirected destination.
    """
    request.session[INERTIA_SESSION_PRESERVE_FRAGMENT] = True


def inertia(
    component: str,
) -> Callable[
    [Callable[..., HttpResponse | InertiaResponse | dict[str, Any]]],
    Callable[..., HttpResponse],
]:
    def decorator(
        func: Callable[..., HttpResponse | InertiaResponse | dict[str, Any]],
    ) -> Callable[..., HttpResponse]:
        @wraps(func)
        def process_inertia_response(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            props = func(request, *args, **kwargs)

            # if a response is returned, return it
            if isinstance(props, HttpResponse):
                return props

            return InertiaResponse(request, component, props)

        return process_inertia_response

    return decorator
