import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from backend.services import reminders


class SendEmailTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {
            "RESEND_API_KEY": "re_test_secret",
            "RESEND_FROM_EMAIL": "Cycle App <mail@example.test>",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("backend.services.reminders.urlopen")
    def test_sends_existing_content_through_resend(self, urlopen):
        urlopen.return_value.__enter__.return_value = None

        reminders.send_email(
            "person@example.test", "Your reminders", "Reminder body"
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, reminders.RESEND_API_URL)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.headers["Authorization"], "Bearer re_test_secret")
        self.assertEqual(json.loads(request.data), {
            "from": "Cycle App <mail@example.test>",
            "to": ["person@example.test"],
            "subject": "Your reminders",
            "text": "Reminder body",
        })
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 20)

    def test_missing_configuration_is_a_safe_configuration_error(self):
        for missing_setting in ("RESEND_API_KEY", "RESEND_FROM_EMAIL"):
            with self.subTest(setting=missing_setting):
                with patch.dict(os.environ, {missing_setting: ""}):
                    with self.assertRaises(reminders.EmailConfigurationError) as raised:
                        reminders.send_email("person@example.test", "subject", "body")

                self.assertIn(missing_setting, str(raised.exception))
                self.assertNotIn("re_test_secret", str(raised.exception))

    @patch("backend.services.reminders.urlopen")
    def test_unverified_sender_error_does_not_expose_provider_body(self, urlopen):
        urlopen.side_effect = HTTPError(
            reminders.RESEND_API_URL,
            403,
            "Forbidden",
            {},
            io.BytesIO(b"raw provider response with secret"),
        )

        with self.assertRaises(reminders.EmailDeliveryError) as raised:
            reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("Verify the sender/domain", str(raised.exception))
        self.assertNotIn("raw provider response", str(raised.exception))

    @patch("backend.services.reminders.urlopen")
    def test_provider_failure_does_not_expose_raw_error(self, urlopen):
        urlopen.side_effect = HTTPError(
            reminders.RESEND_API_URL,
            500,
            "Internal Server Error",
            {},
            io.BytesIO(b"raw provider response with secret"),
        )

        with self.assertRaises(reminders.EmailDeliveryError) as raised:
            reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("Please try again later", str(raised.exception))
        self.assertNotIn("raw provider response", str(raised.exception))

    @patch("backend.services.reminders.urlopen")
    def test_network_error_is_safe_and_user_friendly(self, urlopen):
        urlopen.side_effect = URLError("private network details")

        with self.assertRaises(reminders.EmailDeliveryError) as raised:
            reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("couldn't be reached", str(raised.exception))
        self.assertNotIn("private network details", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
