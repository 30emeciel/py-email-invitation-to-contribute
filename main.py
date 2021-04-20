import base64
import json
import logging
import os
from datetime import datetime, timezone, timedelta

from box import Box
from core.tpl import render
from core.rst_to_html import to_html
from core.mail import send_mail
from core.firestore_client import db
from google.cloud import pubsub_v1

log = logging.getLogger(__name__)

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
TOPIC_NAME = "email-invitation-to-contribute"

publisher = pubsub_v1.PublisherClient()
full_topic_name = f'projects/{PROJECT_ID}/topics/{TOPIC_NAME}'


def from_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    log.debug("""This Function was triggered by messageId {} published at {}
       """.format(context.event_id, context.timestamp))
    event = Box(event)
    if 'data' in event:
        pubsub_message = base64.b64decode(event.data).decode('utf-8')
        log.debug(pubsub_message)
        obj = Box(json.loads(pubsub_message))
        departure_path_id = obj.get("departure_path_id")
        if departure_path_id:
            deferred_email_invitation_to_contribute(departure_path_id)
        else:
            log.warning(f"Invalid message. Missing departure_path_id field")
    else:
        email_invitation_to_contribute()


def defer_email_invitation_to_contribue(departure):
    msg = {
        "departure_path_id": departure.reference.path
    }
    msg_json = json.dumps(msg)
    future = publisher.publish(full_topic_name, base64.b64encode(msg_json.encode("utf-8")))
    return future


def deferred_email_invitation_to_contribute(departure_path_id):
    log.info(f"departure_path_id={departure_path_id}")
    request_doc = db.document(departure_path_id).get()
    assert request_doc.exists
    request = Box(request_doc.to_dict())
    pax_doc = request_doc.reference.parent.parent.get()
    pax = Box(pax_doc.to_dict())
    data = {
        "pax": pax,
        "request": request,
    }
    rst = render("invitation_to_contribute_fr.rst", data)
    title = render("invitation_to_contribute_title_fr.txt", data)

    html = to_html(rst)

    send_mail(f"{pax.name} <{pax.email}>", title, html)


def email_invitation_to_contribute():
    # TODO: fix timestamp in DB!
    a_while_ago = datetime.now(tz=timezone(timedelta(hours=2)))        \
        .replace(hour=0, minute=0, second=0, microsecond=0)             \
        - timedelta(days=2)

    request_departures = db.collection_group('requests') \
        .where('state', "==", "CONFIRMED") \
        .where('departure_date', '==', a_while_ago) \
        .stream()

    futures = (defer_email_invitation_to_contribue(departure) for departure in request_departures)
    for future in futures:
        ret = future.result()
        pass
