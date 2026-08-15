import logging
from functools import wraps
from http import HTTPStatus
from json import dumps as json_encode
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

from .helpers import deep_transform_callables
from .prop_classes import DeferredProp, IgnoreOnFirstLoadProp, MergeableProp, OnceProp
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

    def is_a_partial_render(self, component: str) -> bool:
        return (
            "X-Inertia-Partial-Data" in self.headers
            and self.headers.get("X-Inertia-Partial-Component", "") == component
        )

    def partial_keys(self) -> list[str]:
        return self.headers.get("X-Inertia-Partial-Data", "").split(",")

    def reset_keys(self) -> list[str]:
        return self.headers.get("X-Inertia-Reset", "").split(",")

    def except_once_prop_keys(self) -> list[str]:
        """
        Return the list of once prop keys that the client reports as already
        loaded, sourced from the X-Inertia-Except-Once-Props request header.
        """
        value = self.headers.get("X-Inertia-Except-Once-Props", "")
        if not value:
            return []
        return [k.strip() for k in value.split(",") if k.strip()]

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

        _page: dict[str, Any] = {
            "component": self.component,
            "props": self.build_props(),
            "url": self.request.get_full_path(),
            "version": settings.INERTIA_VERSION,
            "encryptHistory": self.request.should_encrypt_history(),
            "clearHistory": clear_history,
        }

        if should_preserve_fragment:
            _page["preserveFragment"] = True

        _deferred_props = self.build_deferred_props()
        if _deferred_props:
            _page["deferredProps"] = _deferred_props

        _merge_props = self.build_merge_props()
        if _merge_props:
            _page["mergeProps"] = _merge_props

        _prepend_props = self.build_prepend_props()
        if _prepend_props:
            _page["prependProps"] = _prepend_props

        _once_props = self.build_once_props()
        if _once_props:
            _page["onceProps"] = _once_props

        return _page

    def build_props(self) -> Any:
        _props = {
            **(self.request.inertia),
            **self.props,
        }

        _except_once_keys = self.request.except_once_prop_keys()

        for key in list(_props.keys()):
            if self.request.is_a_partial_render(self.component):
                if key not in self.request.partial_keys():
                    del _props[key]
            else:
                prop = _props[key]
                if isinstance(prop, IgnoreOnFirstLoadProp):
                    del _props[key]
                elif (
                    isinstance(prop, OnceProp)
                    and key in _except_once_keys
                    and not prop.should_be_fresh()
                ):
                    # The client already holds this once prop value; skip resolving it
                    del _props[key]

        return deep_transform_callables(_props)

    def build_deferred_props(self) -> dict[str, Any] | None:
        if self.request.is_a_partial_render(self.component):
            return None

        _deferred_props: dict[str, Any] = {}
        for key, prop in self.props.items():
            if isinstance(prop, DeferredProp):
                _deferred_props.setdefault(prop.group, []).append(key)

        return _deferred_props

    def build_merge_props(self) -> list[str]:
        return [
            key
            for key, prop in self.props.items()
            if (
                isinstance(prop, MergeableProp)
                and prop.should_merge()
                and key not in self.request.reset_keys()
            )
        ]

    def build_prepend_props(self) -> list[str]:
        """
        Return merge-able prop keys that should be prepended on the client for
        the current partial reload.

        A non-empty list is only returned when:
        - The request carries X-Inertia-Infinite-Scroll-Merge-Intent: prepend, and
        - The request is a partial reload for the same component.

        The returned keys are the intersection of merge-able props and the props
        explicitly requested in X-Inertia-Partial-Data.
        """
        if self.request.infinite_scroll_merge_intent() != "prepend":
            return []
        if not self.request.is_a_partial_render(self.component):
            return []
        return [
            key
            for key, prop in self.props.items()
            if (
                isinstance(prop, MergeableProp)
                and prop.should_merge()
                and key in self.request.partial_keys()
                and key not in self.request.reset_keys()
            )
        ]

    def build_once_props(self) -> dict[str, Any]:
        """
        Return once prop metadata for inclusion in the page object.

        The onceProps map is only included in full (non-partial) responses.  It
        tells the client which props are once props so it can cache them and
        send their keys in X-Inertia-Except-Once-Props on future requests.

        Each entry maps the prop key to an object containing:
        - prop: the prop name (may differ from the key when custom keys are used)
        - expiresAt: optional expiry timestamp in milliseconds, or null
        """
        if self.request.is_a_partial_render(self.component):
            return {}

        merged = {**self.request.inertia, **self.props}
        return {
            key: {"prop": key, "expiresAt": None}
            for key, prop in merged.items()
            if isinstance(prop, OnceProp)
        }

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

        if self.request.is_inertia():
            _headers = {
                **_headers,
                "Vary": "X-Inertia",
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
