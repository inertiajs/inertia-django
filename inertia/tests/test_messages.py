from inertia.test import InertiaTestCase


class FlashMessagesTestCase(InertiaTestCase):
    def test_messages_are_included_in_top_level_flash_data(self):
        self.inertia.get("/messages/")

        self.assertEqual(
            self.page()["flash"],
            {
                "messages": [
                    {"level": "success", "message": "Profile saved!"},
                ],
            },
        )
        self.assertNotIn("messages", self.props())

    def test_flash_data_is_omitted_when_there_are_no_messages(self):
        self.inertia.get("/no-messages/")

        self.assertNotIn("flash", self.page())

    def test_messages_are_consumed_after_render(self):
        self.inertia.get("/messages/")
        self.assertIn("flash", self.page())

        self.inertia.get("/no-messages/")
        self.assertNotIn("flash", self.page())

    def test_messages_are_included_on_partial_requests(self):
        self.inertia.get(
            "/messages/",
            HTTP_X_INERTIA_PARTIAL_DATA="missing",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        )

        self.assertEqual(
            self.page()["flash"],
            {
                "messages": [
                    {"level": "success", "message": "Profile saved!"},
                ],
            },
        )
