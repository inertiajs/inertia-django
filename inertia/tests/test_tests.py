from inertia.test import InertiaTestCase


class TestTestCase(InertiaTestCase):
    def test_include_props(self):
        self.client.get("/props/")

        self.assertIncludesProps({"name": "Brandon"})

    def test_has_exact_props(self):
        self.client.get("/props/")

        self.assertHasExactProps({"name": "Brandon", "sport": "Hockey"})

    def test_has_template_data(self):
        self.client.get("/template_data/")

        self.assertIncludesTemplateData({"name": "Brian"})

    def test_has_exact_template_data(self):
        self.client.get("/template_data/")

        self.assertHasExactTemplateData({"name": "Brian", "sport": "Basketball"})

    def test_component_name(self):
        self.client.get("/props/")

        self.assertComponentUsed("TestComponent")


class ClientWithLastResponseTrackingTestCase(InertiaTestCase):
    """Tests that ClientWithLastResponse tracks last_response for all HTTP methods."""

    def test_get_updates_last_response(self):
        self.inertia.get("/empty/")
        self.assertIsNotNone(self.inertia.last_response)

    def test_post_updates_last_response(self):
        self.inertia.post("/redirect/")
        self.assertIsNotNone(self.inertia.last_response)

    def test_put_updates_last_response(self):
        self.inertia.put("/redirect/")
        self.assertIsNotNone(self.inertia.last_response)

    def test_patch_updates_last_response(self):
        self.inertia.patch("/redirect/")
        self.assertIsNotNone(self.inertia.last_response)

    def test_delete_updates_last_response(self):
        self.inertia.delete("/redirect/")
        self.assertIsNotNone(self.inertia.last_response)
