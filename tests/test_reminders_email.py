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

    @staticmethod
    def http_error(status, name, message):
        body = json.dumps({
            "statusCode": status,
            "name": name,
            "message": message,
        }).encode("utf-8")
        return HTTPError(
            reminders.RESEND_API_URL,
            status,
            "Provider error",
            {},
            io.BytesIO(body),
        )

    @staticmethod
    def raw_http_error(status, body):
        return HTTPError(
            reminders.RESEND_API_URL,
            status,
            "Provider error",
            {},
            io.BytesIO(body),
        )

    @patch("backend.services.reminders.urlopen")
    def test_sends_existing_content_through_resend(self, urlopen):
        urlopen.return_value.__enter__.return_value.status = 200

        with self.assertLogs("backend.services.reminders", level="INFO") as logs:
            reminders.send_email(
                "person@example.test", "Your reminders", "Sensitive health detail"
            )
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, reminders.RESEND_API_URL)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.headers["Authorization"], "Bearer re_test_secret")
        self.assertEqual(json.loads(request.data), {
            "from": "Cycle App <mail@example.test>",
            "to": ["person@example.test"],
            "subject": "Your reminders",
            "text": "Sensitive health detail",
        })
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 20)
        self.assertIn("status=200", logs.output[0])
        self.assertNotIn("re_test_secret", logs.output[0])
        self.assertNotIn("person@example.test", logs.output[0])
        self.assertNotIn("Sensitive health detail", logs.output[0])

    def test_missing_configuration_is_a_safe_configuration_error(self):
        for missing_setting in ("RESEND_API_KEY", "RESEND_FROM_EMAIL"):
            with self.subTest(setting=missing_setting):
                with patch.dict(os.environ, {missing_setting: ""}):
                    with self.assertRaises(reminders.EmailConfigurationError) as raised:
                        reminders.send_email("person@example.test", "subject", "body")

                self.assertIn(missing_setting, str(raised.exception))
                self.assertNotIn("re_test_secret", str(raised.exception))

    @patch("backend.services.reminders.urlopen")
    def test_onboarding_sender_recipient_restriction_is_explained(self, urlopen):
        provider_message = (
            "You can only send testing emails to your own email address "
            "(person@example.test). Sensitive health detail."
        )
        urlopen.side_effect = self.http_error(403, "validation_error", provider_message)

        with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
            with self.assertRaises(reminders.EmailDeliveryError) as raised:
                reminders.send_email(
                    "person@example.test", "subject", "Sensitive health detail"
                )

        self.assertIn("onboarding sender", str(raised.exception))
        self.assertIn("verify a domain", str(raised.exception))
        self.assertIn("status=403", logs.output[0])
        self.assertIn("error_type=validation_error", logs.output[0])
        self.assertIn("category=test_recipient_restriction", logs.output[0])
        self.assertIn('"statusCode":403', logs.output[0])
        self.assertNotIn(provider_message, logs.output[0])
        self.assertNotIn("person@example.test", logs.output[0])
        self.assertNotIn("Sensitive health detail", logs.output[0])

    @patch("backend.services.reminders.urlopen")
    def test_unverified_sender_is_logged_without_provider_message(self, urlopen):
        provider_message = "The sender domain is not verified: person@example.test."
        urlopen.side_effect = self.http_error(403, "validation_error", provider_message)

        with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
            with self.assertRaises(reminders.EmailDeliveryError) as raised:
                reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("verified sender", str(raised.exception))
        self.assertIn("status=403", logs.output[0])
        self.assertIn("category=sender_or_request_rejected", logs.output[0])
        self.assertIn('"message":"The sender domain is not verified: [redacted email]."',
                      logs.output[0])
        self.assertNotIn(provider_message, logs.output[0])
        self.assertNotIn("person@example.test", logs.output[0])

    @patch("backend.services.reminders.urlopen")
    def test_http_error_statuses_and_provider_bodies_are_logged(self, urlopen):
        cases = [
            (400, "validation_error", "Invalid request field."),
            (401, "invalid_api_key", "API key is invalid."),
            (403, "validation_error", "Sender is not permitted."),
            (422, "validation_error", "Sender address is not verified."),
        ]
        for status, name, message in cases:
            with self.subTest(status=status):
                urlopen.side_effect = self.http_error(status, name, message)
                expected_body = json.dumps({
                    "statusCode": status,
                    "name": name,
                    "message": message,
                })

                with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
                    with self.assertRaises(reminders.EmailDeliveryError):
                        reminders.send_email("person@example.test", "subject", "body")

                self.assertIn("status=" + str(status), logs.output[0])
                self.assertIn("response_body=" + expected_body, logs.output[0])
                self.assertNotIn("re_test_secret", logs.output[0])
                self.assertNotIn("Bearer", logs.output[0])

    @patch("backend.services.reminders.urlopen")
    def test_empty_and_unparseable_provider_bodies_are_distinguished(self, urlopen):
        cases = [
            (b"", "response_body_state=empty", "response_body_bytes=0"),
            (
                b"private non-json response",
                "response_body_state=non_json",
                "response_body_bytes=25",
            ),
        ]
        for body, expected_state, expected_size in cases:
            with self.subTest(expected_state=expected_state):
                urlopen.side_effect = self.raw_http_error(403, body)

                with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
                    with self.assertRaises(reminders.EmailDeliveryError):
                        reminders.send_email("person@example.test", "subject", "body")

                self.assertIn(expected_state, logs.output[0])
                self.assertIn(expected_size, logs.output[0])
                self.assertIn("error_type=unspecified", logs.output[0])
                self.assertNotIn("private non-json response", logs.output[0])

    @patch("backend.services.reminders.urlopen")
    def test_provider_failure_does_not_expose_raw_error(self, urlopen):
        provider_message = "Internal issue. Sensitive health detail."
        urlopen.side_effect = self.http_error(500, "internal_server_error", provider_message)

        with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
            with self.assertRaises(reminders.EmailDeliveryError) as raised:
                reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("Please try again later", str(raised.exception))
        self.assertIn("status=500", logs.output[0])
        self.assertNotIn(provider_message, logs.output[0])
        self.assertNotIn("Sensitive health detail", logs.output[0])

    @patch("backend.services.reminders.urlopen")
    def test_network_error_is_safe_and_user_friendly(self, urlopen):
        urlopen.side_effect = URLError("private network details")

        with self.assertLogs("backend.services.reminders", level="WARNING") as logs:
            with self.assertRaises(reminders.EmailDeliveryError) as raised:
                reminders.send_email("person@example.test", "subject", "body")

        self.assertIn("couldn't be reached", str(raised.exception))
        self.assertNotIn("private network details", str(raised.exception))
        self.assertIn("error_type=URLError", logs.output[0])


if __name__ == "__main__":
    unittest.main()
