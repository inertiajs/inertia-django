from inertia.test import InertiaTestCase, inertia_page


class OncePropsTestCase(InertiaTestCase):
    """Tests for the once prop feature introduced in Inertia v3.

    Once props are resolved on the initial visit and cached by the client.
    On subsequent visits the client sends the cached keys via
    X-Inertia-Except-Once-Props so the server can skip re-resolving them.
    """

    def test_once_props_are_included_on_first_load(self):
        """Without X-Inertia-Except-Once-Props the prop is resolved normally."""
        self.assertJSONResponse(
            self.inertia.get("/once/"),
            inertia_page(
                "once",
                props={"name": "Brandon", "plans": ["basic", "pro"]},
                once_props={"plans": {"prop": "plans", "expiresAt": None}},
            ),
        )

    def test_once_props_metadata_is_included_on_first_load(self):
        """The onceProps key is present in the full page response."""
        response = self.inertia.get("/once/")
        page = response.json()

        self.assertIn("onceProps", page)
        self.assertEqual(
            page["onceProps"],
            {"plans": {"prop": "plans", "expiresAt": None}},
        )

    def test_once_props_are_skipped_when_client_already_has_them(self):
        """When the client sends the key in X-Inertia-Except-Once-Props the
        prop is excluded from the response props but the onceProps metadata
        is still included so the client can continue to track the key."""
        response = self.inertia.get(
            "/once/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans",
        )
        page = response.json()

        self.assertNotIn("plans", page["props"])
        self.assertIn("name", page["props"])
        self.assertIn("onceProps", page)
        self.assertIn("plans", page["onceProps"])

    def test_once_props_are_skipped_for_multiple_keys(self):
        """Multiple comma-separated keys in X-Inertia-Except-Once-Props are
        all respected."""
        response = self.inertia.get(
            "/once/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans,other",
        )
        page = response.json()

        self.assertNotIn("plans", page["props"])

    def test_once_props_metadata_is_included_for_selected_partial_props(self):
        """Selected once props retain metadata on partial responses so the
        client can continue to track its cache entry."""
        response = self.inertia.get(
            "/once/",
            HTTP_X_INERTIA_PARTIAL_DATA="plans",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        )
        page = response.json()

        self.assertEqual(
            page["onceProps"],
            {"plans": {"prop": "plans", "expiresAt": None}},
        )

    def test_once_props_are_resolved_on_explicit_partial_reload(self):
        """Even when listed in X-Inertia-Except-Once-Props a once prop is
        resolved when it is explicitly requested via partial reload."""
        response = self.inertia.get(
            "/once/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans",
            HTTP_X_INERTIA_PARTIAL_DATA="plans",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        )
        page = response.json()

        self.assertIn("plans", page["props"])
        self.assertEqual(page["props"]["plans"], ["basic", "pro"])

    def test_fresh_once_props_are_always_resolved(self):
        """A once prop created with fresh=True is always resolved even when
        the client reports having it via X-Inertia-Except-Once-Props."""
        self.assertJSONResponse(
            self.inertia.get(
                "/once-fresh/",
                HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans",
            ),
            inertia_page(
                "once-fresh",
                props={"name": "Brandon", "plans": ["basic", "pro"]},
                once_props={"plans": {"prop": "plans", "expiresAt": None}},
            ),
        )

    def test_once_props_full_page_initial_load_includes_value(self):
        """A full (non-Inertia) page request also includes the once prop value
        in the serialised page data embedded in the HTML."""
        response = self.client.get("/once/")
        self.assertContains(response, "basic")
        self.assertContains(response, "pro")

    def test_empty_except_once_props_header_is_handled_gracefully(self):
        """An empty X-Inertia-Except-Once-Props header does not raise an
        exception and behaves as if the header were absent."""
        response = self.inertia.get(
            "/once/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="",
        )
        page = response.json()

        self.assertIn("plans", page["props"])


class SharedOncePropsTestCase(InertiaTestCase):
    """Tests that once props set via share() are handled correctly.

    Once props in shared data must appear in the onceProps metadata so the
    client knows to cache them, and must be skipped on subsequent requests
    when the client reports holding them via X-Inertia-Except-Once-Props.
    """

    def test_shared_once_props_metadata_is_included(self):
        """A once prop set via share() appears in onceProps on the first load."""
        response = self.inertia.get("/once-shared/")
        page = response.json()

        self.assertIn("onceProps", page)
        self.assertIn("plans", page["onceProps"])

    def test_shared_once_props_value_is_resolved_on_first_load(self):
        """The value of a shared once prop is present in props on first load."""
        response = self.inertia.get("/once-shared/")
        page = response.json()

        self.assertIn("plans", page["props"])
        self.assertEqual(page["props"]["plans"], ["basic", "pro"])

    def test_shared_once_props_are_skipped_when_client_has_them(self):
        """A shared once prop is excluded from props when the client reports
        holding it via X-Inertia-Except-Once-Props."""
        response = self.inertia.get(
            "/once-shared/",
            HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans",
        )
        page = response.json()

        self.assertNotIn("plans", page["props"])
        self.assertIn("onceProps", page)
        self.assertIn("plans", page["onceProps"])


class CallablePropStaticValueTestCase(InertiaTestCase):
    """Tests that prop classes correctly handle plain (non-callable) values.

    CallableProp.__call__ has two branches: one for callables (the common case)
    and one for plain values passed directly.  Views that pass a static value
    to once(), merge(), or defer() exercise the second branch.
    """

    def test_once_prop_with_static_value_is_resolved(self):
        """A once prop wrapping a plain value (not a callable) is resolved
        correctly on first load."""
        from inertia.prop_classes import OnceProp

        prop = OnceProp(["basic", "pro"])
        self.assertEqual(prop(), ["basic", "pro"])

    def test_callable_prop_with_callable_is_resolved(self):
        """Sanity check: a callable is still invoked by __call__."""
        from inertia.prop_classes import OnceProp

        prop = OnceProp(lambda: ["basic", "pro"])
        self.assertEqual(prop(), ["basic", "pro"])
