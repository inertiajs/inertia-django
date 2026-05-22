import json

from inertia.test import InertiaTestCase, inertia_page

# ---------------------------------------------------------------------------
# preserveFragment
# ---------------------------------------------------------------------------


class PreserveFragmentTestCase(InertiaTestCase):
    """Tests for server-side preserveFragment support introduced in Inertia v3.

    When a view calls preserve_fragment(request) before returning, the
    subsequent Inertia page response will include preserveFragment: true in
    the page object.  The client uses this to retain the original URL fragment
    across the redirect.
    """

    def test_preserve_fragment_is_included_when_set(self):
        """preserve_fragment(request) causes preserveFragment: true to appear
        in the rendered page object."""
        self.assertJSONResponse(
            self.inertia.get("/preserve-fragment/"),
            inertia_page(
                "preserve-fragment",
                props={"name": "Brandon"},
                preserve_fragment=True,
            ),
        )

    def test_preserve_fragment_is_absent_by_default(self):
        """preserveFragment is not in the page object when not requested."""
        response = self.inertia.get("/empty/")
        page = response.json()

        self.assertNotIn("preserveFragment", page)

    def test_preserve_fragment_persists_across_a_redirect(self):
        """When preserve_fragment is called before a redirect the flag
        survives in the session and is included in the page response that
        follows the redirect."""
        self.inertia.get("/preserve-fragment-redirect/", follow=True)
        page = self.inertia.last_response.json()

        self.assertTrue(page.get("preserveFragment"))

    def test_preserve_fragment_is_consumed_after_one_response(self):
        """The session flag is cleared after the first response that reads it,
        so a second request does not see preserveFragment: true."""
        self.inertia.get("/preserve-fragment/")
        response = self.inertia.get("/empty/")
        page = response.json()

        self.assertNotIn("preserveFragment", page)

    def test_preserve_fragment_type_error_raises(self):
        """A non-bool session value raises TypeError, matching the contract of
        the other session-based flags."""
        with self.assertRaises(TypeError):
            self.inertia.get("/preserve-fragment-type-error/")


# ---------------------------------------------------------------------------
# preserveErrors via partial reload filtering
# ---------------------------------------------------------------------------


class PreserveErrorsTestCase(InertiaTestCase):
    """Tests that verify preserveErrors behaviour for partial reloads.

    The Django adapter already filters shared props through the partial reload
    mechanism.  When the client sends a partial reload that does not include
    the errors key, the shared errors prop is excluded from the response.
    This allows the client-side preserveErrors option to work correctly:
    the server will not overwrite the client's existing errors with an empty
    dict unless the client explicitly requests the errors key.
    """

    def test_shared_errors_are_included_on_full_render(self):
        """Shared errors are present on a full (non-partial) Inertia render."""
        response = self.inertia.get("/preserve-errors/")
        page = response.json()

        self.assertIn("errors", page["props"])
        self.assertEqual(page["props"]["errors"], {"email": "required"})

    def test_shared_errors_are_excluded_from_partial_reload_by_default(self):
        """When errors is not in X-Inertia-Partial-Data the shared errors
        prop is omitted from the partial reload response, ensuring the client's
        preserveErrors option can retain its existing errors."""
        response = self.inertia.get(
            "/preserve-errors/",
            HTTP_X_INERTIA_PARTIAL_DATA="name",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        )
        page = response.json()

        self.assertIn("name", page["props"])
        self.assertNotIn("errors", page["props"])

    def test_shared_errors_are_included_when_explicitly_requested(self):
        """A partial reload that includes errors in X-Inertia-Partial-Data
        does receive the errors prop."""
        response = self.inertia.get(
            "/preserve-errors/",
            HTTP_X_INERTIA_PARTIAL_DATA="errors",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        )
        page = response.json()

        self.assertIn("errors", page["props"])


# ---------------------------------------------------------------------------
# Infinite scroll merge intent
# ---------------------------------------------------------------------------


class InfiniteScrollMergeIntentTestCase(InertiaTestCase):
    """Tests for the X-Inertia-Infinite-Scroll-Merge-Intent request header.

    When the client sends this header with the value prepend during a partial
    reload for merge-able props, the response should include a prependProps
    list so the client knows to prepend the new data rather than append it.
    """

    def test_merge_props_are_in_merge_props_without_intent_header(self):
        """Without X-Inertia-Infinite-Scroll-Merge-Intent the merge-able
        prop is listed in mergeProps as normal."""
        self.assertJSONResponse(
            self.inertia.get("/infinite-scroll/"),
            inertia_page(
                "infinite-scroll",
                props={"name": "Brandon", "items": ["item1", "item2"]},
                merge_props=["items"],
            ),
        )

    def test_append_intent_does_not_produce_prepend_props(self):
        """An explicit append intent header does not produce prependProps."""
        response = self.inertia.get(
            "/infinite-scroll/",
            HTTP_X_INERTIA_PARTIAL_DATA="items",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_INFINITE_SCROLL_MERGE_INTENT="append",
        )
        page = response.json()

        self.assertNotIn("prependProps", page)

    def test_prepend_intent_produces_prepend_props(self):
        """When the merge intent is prepend, prependProps is included in the
        partial reload response with the requested merge-able prop keys."""
        response = self.inertia.get(
            "/infinite-scroll/",
            HTTP_X_INERTIA_PARTIAL_DATA="items",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_INFINITE_SCROLL_MERGE_INTENT="prepend",
        )
        page = response.json()

        self.assertIn("prependProps", page)
        self.assertIn("items", page["prependProps"])

    def test_prepend_intent_on_non_partial_render_produces_no_prepend_props(self):
        """prependProps is never produced on a full (non-partial) render even
        when the intent header is present, because there is no meaningful
        merge operation on a first load."""
        response = self.inertia.get(
            "/infinite-scroll/",
            HTTP_X_INERTIA_INFINITE_SCROLL_MERGE_INTENT="prepend",
        )
        page = response.json()

        self.assertNotIn("prependProps", page)

    def test_prepend_intent_excludes_non_merge_props_from_prepend_props(self):
        """Only merge-able props requested in the partial data are included
        in prependProps; regular props are not listed there."""
        response = self.inertia.get(
            "/infinite-scroll/",
            HTTP_X_INERTIA_PARTIAL_DATA="name,items",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_INFINITE_SCROLL_MERGE_INTENT="prepend",
        )
        page = response.json()

        self.assertIn("prependProps", page)
        self.assertIn("items", page["prependProps"])
        self.assertNotIn("name", page["prependProps"])

    def test_prepend_props_respects_reset_keys(self):
        """A key listed in X-Inertia-Reset is excluded from prependProps."""
        response = self.inertia.get(
            "/infinite-scroll/",
            HTTP_X_INERTIA_PARTIAL_DATA="items",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
            HTTP_X_INERTIA_INFINITE_SCROLL_MERGE_INTENT="prepend",
            HTTP_X_INERTIA_RESET="items",
        )
        page = response.json()

        self.assertNotIn("prependProps", page)


# ---------------------------------------------------------------------------
# useHttp CSRF
# ---------------------------------------------------------------------------


class UseHttpCsrfTestCase(InertiaTestCase):
    """Tests that verify CSRF token availability for useHttp (non-visit XHR).

    useHttp requests do not carry the X-Inertia header.  The middleware must
    still set the CSRF cookie so the client can include the token in its
    request headers.
    """

    def test_csrf_token_is_set_for_non_inertia_requests(self):
        """A plain (non-Inertia) request receives a CSRF cookie, enabling
        useHttp requests to include the token."""
        response = self.client.get("/props/")
        self.assertIsNotNone(response.cookies.get("csrftoken"))

    def test_csrf_token_is_set_for_inertia_requests(self):
        """Inertia-flagged requests also receive the CSRF cookie."""
        response = self.inertia.get("/props/")
        self.assertIsNotNone(response.cookies.get("csrftoken"))

    def test_non_inertia_response_is_not_modified_by_middleware(self):
        """The middleware does not alter the status or content of a response
        to a plain HTTP request, which is the path taken by useHttp."""
        response = self.client.get("/test/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("X-Inertia", response.headers)

    def test_non_inertia_4xx_responses_pass_through_unchanged(self):
        """A 422 JSON response returned by a view for a useHttp validation
        error is forwarded to the client without modification."""
        from django.http import JsonResponse

        from inertia.middleware import InertiaMiddleware

        class FakeGet:
            def __call__(self, request):
                return JsonResponse({"errors": {"email": "required"}}, status=422)

        middleware = InertiaMiddleware(FakeGet())

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post(
            "/api/submit/",
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = middleware(request)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            json.loads(response.content), {"errors": {"email": "required"}}
        )

    def test_non_inertia_redirect_passes_through_unchanged(self):
        """A redirect response from a view that handles a useHttp request is
        forwarded as-is; the middleware does not change its status code."""
        from django.http import HttpResponseRedirect

        from inertia.middleware import InertiaMiddleware

        class FakeGet:
            def __call__(self, request):
                return HttpResponseRedirect("/login/")

        middleware = InertiaMiddleware(FakeGet())

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post(
            "/api/submit/",
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")
