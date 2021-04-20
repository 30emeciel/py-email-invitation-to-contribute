import base64
import json
from unittest import TestCase

import dotenv
from box import Box


class Test(TestCase):
    def setUp(self) -> None:
        dotenv.load_dotenv()

    def test_email_invitation_to_contribute(self):
        from main import email_invitation_to_contribute
        email_invitation_to_contribute()

    def test_deferred_email_invitation_to_contribute(self):
        from main import deferred_email_invitation_to_contribute
        deferred_email_invitation_to_contribute('pax/google-oauth2|107336710838050909583/requests/KHQpVVu1H7Hvn3jLwX01')

    def test_from_pubsub(self):
        from main import from_pubsub
        msg = {
            "departure_path_id": 'pax/google-oauth2|107336710838050909583/requests/KHQpVVu1H7Hvn3jLwX01'
        }
        msg_json = json.dumps(msg)

        event = {
            "data": base64.b64encode(msg_json.encode("utf-8"))
        }
        context = Box({
            "event_id": "event_id",
            "timestamp": "timestamp",
        })
        from_pubsub(event, context)

