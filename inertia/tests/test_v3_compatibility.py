from datetime import datetime, timezone

from django.http import HttpResponseRedirect
from django.test import RequestFactory

from inertia import merge, once
from inertia.middleware import InertiaMiddleware
from inertia.test import InertiaTestCase


class V3PropsCompatibilityTestCase(InertiaTestCase):
    def test_partial_except_supports_nested_paths(self):
        page = self.inertia.get(
            "/v3/nested/",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_PARTIAL_EXCEPT="user.token",
        ).json()

        self.assertEqual(page["props"]["user"], {"name": "Brandon"})
        self.assertEqual(page["props"]["config"]["timezone"], "UTC")

    def test_partial_only_supports_nested_once_props(self):
        page = self.inertia.get(
            "/v3/nested/",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_PARTIAL_DATA="config.locale",
        ).json()

        self.assertEqual(page["props"], {"config": {"locale": "en-US"}})
        self.assertEqual(
            page["onceProps"], {"locale": {"prop": "config.locale", "expiresAt": None}}
        )

    def test_cached_once_props_are_not_refreshed_by_partial_except(self):
        page = self.inertia.get(
            "/v3/nested/",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_PARTIAL_EXCEPT="user.token",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="locale",
        ).json()

        self.assertEqual(page["props"]["config"], {"timezone": "UTC"})
        self.assertEqual(
            page["onceProps"], {"locale": {"prop": "config.locale", "expiresAt": None}}
        )

    def test_merge_prepend_does_not_require_append_false(self):
        nested = merge(lambda: [], prepend="items")
        root = merge(lambda: [], prepend=True)

        self.assertEqual(nested.merge_paths("feed", prepend=True), ["feed.items"])
        self.assertEqual(nested.merge_paths("feed"), [])
        self.assertEqual(root.merge_paths("feed", prepend=True), ["feed"])

    def test_merge_metadata_supports_nested_paths_and_matching(self):
        page = self.inertia.get("/v3/merge/").json()

        self.assertEqual(page["mergeProps"], ["feed.items"])
        self.assertEqual(page["deepMergeProps"], ["chat"])
        self.assertEqual(page["matchPropsOn"], ["feed.items.id", "chat.messages.id"])

    def test_scroll_metadata_is_emitted(self):
        page = self.inertia.get("/v3/scroll/").json()

        self.assertEqual(page["mergeProps"], ["players"])
        self.assertEqual(
            page["scrollProps"]["players"],
            {
                "pageName": "page",
                "previousPage": None,
                "nextPage": 2,
                "currentPage": 1,
                "reset": False,
            },
        )

    def test_deferred_scroll_is_loaded_as_a_deferred_prop(self):
        page = self.inertia.get("/v3/deferred-scroll/").json()

        self.assertEqual(page["props"], {"score": "Brandon"})
        self.assertEqual(page["deferredProps"], {"default": ["players"]})
        self.assertEqual(page["mergeProps"], ["players"])
        self.assertEqual(page["scrollProps"]["players"]["nextPage"], 2)

        partial_page = self.inertia.get(
            "/v3/deferred-scroll/",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_PARTIAL_DATA="players",
        ).json()

        self.assertEqual(
            partial_page["props"], {"score": "Brandon", "players": ["Brian", "Brandon"]}
        )
        self.assertEqual(partial_page["mergeProps"], ["players"])
        self.assertEqual(partial_page["scrollProps"]["players"]["nextPage"], 2)

    def test_cached_deferred_once_prop_is_not_advertised_as_deferred(self):
        initial_page = self.inertia.get("/v3/deferred-once/").json()

        self.assertEqual(initial_page["props"], {})
        self.assertEqual(initial_page["deferredProps"], {"default": ["report"]})
        self.assertEqual(
            initial_page["onceProps"],
            {"cached-report": {"prop": "report", "expiresAt": None}},
        )

        cached_page = self.inertia.get(
            "/v3/deferred-once/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="cached-report",
        ).json()

        self.assertEqual(cached_page["props"], {})
        self.assertNotIn("deferredProps", cached_page)
        self.assertEqual(
            cached_page["onceProps"],
            {"cached-report": {"prop": "report", "expiresAt": None}},
        )

    def test_always_prop_is_included_in_partial_reloads(self):
        page = self.inertia.get(
            "/v3/deferred-scroll/",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_PARTIAL_DATA="players",
        ).json()

        self.assertEqual(page["props"]["score"], "Brandon")

    def test_django_messages_are_added_to_the_page_not_props(self):
        page = self.inertia.get("/messages/").json()

        self.assertEqual(
            page["flash"],
            {"messages": [{"level": "success", "message": "Profile saved!"}]},
        )
        self.assertNotIn("flash", page["props"])

    def test_once_supports_custom_keys_and_expiration(self):
        expires_at = datetime(2030, 1, 1, tzinfo=timezone.utc)
        prop = once(lambda: "Hockey", key="favorite-sport", expires_at=expires_at)

        self.assertEqual(prop.once_key("sport"), "favorite-sport")
        self.assertEqual(prop.once_expires_at(), 1893456000000)


class V3MiddlewareCompatibilityTestCase(InertiaTestCase):
    def test_inertia_fragment_redirect_uses_protocol_response(self):
        middleware = InertiaMiddleware(
            lambda request: HttpResponseRedirect("/players#goalies")
        )
        response = middleware(RequestFactory().get("/players", HTTP_X_INERTIA="true"))

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response["X-Inertia-Redirect"], "/players#goalies")

    def test_version_mismatches_do_not_replace_post_responses(self):
        middleware = InertiaMiddleware(lambda request: HttpResponseRedirect("/players"))
        response = middleware(
            RequestFactory().post(
                "/players", HTTP_X_INERTIA="true", HTTP_X_INERTIA_VERSION="stale"
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_stale_get_takes_priority_over_fragment_redirect(self):
        middleware = InertiaMiddleware(
            lambda request: HttpResponseRedirect("/players#goalies")
        )
        response = middleware(
            RequestFactory().get(
                "/players", HTTP_X_INERTIA="true", HTTP_X_INERTIA_VERSION="stale"
            )
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response["X-Inertia-Location"], "http://testserver/players")
        self.assertNotIn("X-Inertia-Redirect", response)

    def test_non_post_fragment_redirect_uses_protocol_response(self):
        middleware = InertiaMiddleware(
            lambda request: HttpResponseRedirect("/players#goalies")
        )

        for method in ("put", "patch", "delete"):
            with self.subTest(method=method):
                request = getattr(RequestFactory(), method)(
                    "/players", HTTP_X_INERTIA="true"
                )
                response = middleware(request)

                self.assertEqual(response.status_code, 409)
                self.assertEqual(response["X-Inertia-Redirect"], "/players#goalies")
