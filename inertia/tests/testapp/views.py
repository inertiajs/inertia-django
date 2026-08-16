from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware

from inertia import (
    always,
    deep_merge,
    defer,
    inertia,
    lazy,
    location,
    merge,
    once,
    optional,
    preserve_fragment,
    render,
    scroll,
    share,
)
from inertia.http import (
    INERTIA_SESSION_CLEAR_HISTORY,
    INERTIA_SESSION_PRESERVE_FRAGMENT,
    clear_history,
    encrypt_history,
)


class ShareMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        share(
            request,
            position=lambda: "goalie",
            number=29,
        )


def test(request):
    return HttpResponse("Hey good stuff")


@inertia("TestComponent")
def empty_test(request):
    return {}


def redirect_test(request):
    return redirect(empty_test)


@inertia("TestComponent")
def inertia_redirect_test(request):
    return redirect(empty_test)


def external_redirect_test(request):
    return location("http://foobar.com/")


@inertia("TestComponent")
def props_test(request):
    return {
        "name": "Brandon",
        "sport": "Hockey",
    }


def template_data_test(request):
    return render(
        request,
        "TestComponent",
        template_data={
            "name": "Brian",
            "sport": "Basketball",
        },
    )


@inertia("TestComponent")
def lazy_test(request):
    return {
        "name": "Brian",
        "sport": lazy(lambda: "Basketball"),
        "grit": lazy(lambda: "intense"),
    }


@inertia("TestComponent")
def optional_test(request):
    return {
        "name": "Brian",
        "sport": optional(lambda: "Basketball"),
        "grit": optional(lambda: "intense"),
    }


@inertia("TestComponent")
def defer_test(request):
    return {"name": "Brian", "sport": defer(lambda: "Basketball")}


@inertia("TestComponent")
def defer_group_test(request):
    return {
        "name": "Brian",
        "sport": defer(lambda: "Basketball", "group"),
        "team": defer(lambda: "Bulls", "group"),
        "grit": defer(lambda: "intense"),
    }


@inertia("TestComponent")
def merge_test(request):
    return {
        "name": "Brandon",
        "sport": merge(lambda: "Hockey"),
        "team": defer(lambda: "Penguins", merge=True),
    }


@inertia("TestComponent")
def complex_props_test(request):
    return {
        "person": {
            "name": lambda: "Brandon",
        }
    }


@decorator_from_middleware(ShareMiddleware)
@inertia("TestComponent")
def share_test(request):
    return {
        "name": "Brandon",
    }


@inertia("TestComponent")
def encrypt_history_test(request):
    encrypt_history(request)
    return {}


@inertia("TestComponent")
def encrypt_history_false_test(request):
    encrypt_history(request, False)
    return {}


@inertia("TestComponent")
def encrypt_history_type_error_test(request):
    encrypt_history(request, "foo")
    return {}


@inertia("TestComponent")
def clear_history_test(request):
    clear_history(request)
    return {}


@inertia("TestComponent")
def clear_history_redirect_test(request):
    clear_history(request)
    return redirect(empty_test)


@inertia("TestComponent")
def clear_history_type_error_test(request):
    request.session[INERTIA_SESSION_CLEAR_HISTORY] = "foo"
    return {}


# ---------------------------------------------------------------------------
# Once props (Inertia v3)
# ---------------------------------------------------------------------------


@inertia("TestComponent")
def once_test(request):
    return {
        "name": "Brandon",
        "plans": once(lambda: ["basic", "pro"]),
    }


@inertia("TestComponent")
def once_shared_test(request):
    """Exercises once props set via share() to verify they appear in onceProps
    metadata and are correctly skipped when the client already holds them."""
    share(request, plans=once(lambda: ["basic", "pro"]))
    return {"name": "Brandon"}


@inertia("TestComponent")
def once_fresh_test(request):
    return {
        "name": "Brandon",
        "plans": once(lambda: ["basic", "pro"], fresh=True),
    }


# ---------------------------------------------------------------------------
# preserveFragment (Inertia v3)
# ---------------------------------------------------------------------------


@inertia("TestComponent")
def preserve_fragment_page_test(request):
    """Simulates the page rendered after following a redirect that had
    preserve_fragment set on the preceding response."""
    preserve_fragment(request)
    return {"name": "Brandon"}


def preserve_fragment_redirect_test(request):
    """Sets preserve_fragment and issues a redirect; the flag travels via
    the session to the next Inertia response."""
    preserve_fragment(request)
    return redirect(empty_test)


@inertia("TestComponent")
def preserve_fragment_type_error_test(request):
    request.session[INERTIA_SESSION_PRESERVE_FRAGMENT] = "not-a-bool"
    return {}


# ---------------------------------------------------------------------------
# preserveErrors / shared errors partial-reload filtering (Inertia v3)
# ---------------------------------------------------------------------------


class ShareErrorsMiddleware:
    """Shares an errors prop to simulate form validation errors in shared
    data.  Used to verify that partial reloads correctly exclude shared
    errors when they are not in X-Inertia-Partial-Data."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        share(request, errors={"email": "required"})


@decorator_from_middleware(ShareErrorsMiddleware)
@inertia("TestComponent")
def preserve_errors_test(request):
    return {"name": "Brandon"}


# ---------------------------------------------------------------------------
# Infinite scroll / X-Inertia-Infinite-Scroll-Merge-Intent (Inertia v3)
# ---------------------------------------------------------------------------


@inertia("TestComponent")
def infinite_scroll_test(request):
    return {
        "name": "Brandon",
        "items": merge(lambda: ["item1", "item2"]),
    }


@inertia("TestComponent")
def v3_nested_props_test(request):
    return {
        "config": {
            "locale": once(lambda: "en-US", key="locale"),
            "timezone": "UTC",
        },
        "user": {"name": "Brandon", "token": "secret-token"},
    }


@inertia("TestComponent")
def v3_merge_props_test(request):
    return {
        "feed": merge(
            lambda: {"items": [{"id": 2, "name": "Brandon"}]},
            append="items",
            match_on="items.id",
        ),
        "chat": deep_merge(
            lambda: {"messages": [{"id": 2, "body": "Hockey"}]},
            match_on="messages.id",
        ),
    }


@inertia("TestComponent")
def v3_scroll_test(request):
    return {
        "players": scroll(
            lambda: ["Brian", "Brandon"],
            {
                "pageName": "page",
                "previousPage": None,
                "nextPage": 2,
                "currentPage": 1,
            },
        )
    }


@inertia("TestComponent")
def v3_deferred_scroll_test(request):
    return {
        "score": always(lambda: "Brandon"),
        "players": scroll(
            lambda: ["Brian", "Brandon"],
            {
                "pageName": "page",
                "previousPage": None,
                "nextPage": 2,
                "currentPage": 1,
            },
            defer=True,
        ),
    }


@inertia("TestComponent")
def v3_deferred_once_test(request):
    return {
        "report": defer(
            lambda: {"winner": "Brandon"},
            once=True,
            key="cached-report",
        )
    }


@inertia("TestComponent")
def messages_test(request):
    messages.success(request, "Profile saved!")
    return {}


@inertia("TestComponent")
def no_messages_test(request):
    return {}
