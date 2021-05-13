import base64
import json
import pickle
from datetime import datetime, timezone, timedelta

import dotenv
import pytest
from box import Box
from core import firestore_client
from core.mailer import Mailer
from google.cloud import pubsub_v1
from google.cloud.firestore_v1 import Client
from google.cloud.pubsub_v1.publisher.futures import Future
from mockito import mock


@pytest.fixture(autouse=True)
def setup():
    dotenv.load_dotenv()


@pytest.fixture(autouse=False)
def db(when):
    ret = mock(Client)
    when(firestore_client).db().thenReturn(ret)
    return ret


def test_email_invitation_to_contribute(when):
    import main
    future = mock(Future)
    when(main).defer_email_invitation_to_contribue(...).thenReturn(future)
    when(future).result().thenReturn()
    # a_while_ago = datetime(2021, 5, 5, 00, 00, 00, tzinfo=timezone(timedelta(hours=2)))
    main.email_invitation_to_contribute()


def test_defer_invitation_to_contribute(when):
    publisher = pubsub_v1.PublisherClient()
    when(publisher).publish(...).thenReturn()
    import main
    main.defer_email_invitation_to_contribue(
        'pax/auth0|60944beb668f990071383b74',
        datetime(2021, 5, 5, 00, 00, 00, tzinfo=timezone(timedelta(hours=2)))
    )


def _write_html(html):
    with open("test.html", mode='wb') as f:
        f.write(html.encode("utf-8"))


def test_deferred_email_invitation_to_contribute(when, patch):
    patch(Mailer.send_mail, lambda pax_name, pax_email, title, html: _write_html(html))
    import main
    main.deferred_email_invitation_to_contribute(
        'pax/auth0|5ff87d92a54dd0006f957407',
        datetime(2021, 5, 5, 00, 00, 00, tzinfo=timezone(timedelta(hours=2)))
    )
    #'pax/google-oauth2|107336710838050909583/requests/KHQpVVu1H7Hvn3jLwX01')


def test_from_pubsub(when, patch):
    patch(Mailer.send_mail, lambda pax_name, pax_email, title, html: _write_html(html))

    from main import from_pubsub
    args = [
        'pax/auth0|5ff87d92a54dd0006f957407',
        datetime(2021, 5, 5, 00, 00, 00, tzinfo=timezone(timedelta(hours=2))).timestamp()
    ]

    event = {
        "data": base64.b64encode(json.dumps(args).encode("utf-8"))
    }
    context = Box({
        "event_id": "event_id",
        "timestamp": "timestamp",
    })
    from_pubsub(event, context)

