from inertia.test import InertiaTestCase


class FlashMessagesTestCase(InertiaTestCase):
    def test_success_message_included_in_props(self):
        self.inertia.get("/messages/")
        self.assertIncludesProps({
            "messages": [{"level": "success", "message": "Profile saved!"}]
        })

    def test_no_messages_key_when_no_messages(self):
        self.inertia.get("/no-messages/")
        self.assertNotIn("messages", self.props())

    def test_messages_consumed_after_render(self):
        # First request — message should be present
        self.inertia.get("/messages/")
        self.assertIncludesProps({
            "messages": [{"level": "success", "message": "Profile saved!"}]
        })

        # Second request to a view with no messages — should not carry over
        self.inertia.get("/no-messages/")
        self.assertNotIn("messages", self.props())
