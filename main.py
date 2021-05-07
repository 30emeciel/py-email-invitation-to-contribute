import base64
import logging
import os
import pickle
from datetime import datetime, timezone, timedelta

from box import Box
from core import firestore_client
from core.mailer import Mailer
from core.rst_to_html import to_html
from core.tpl import render
from firebase_admin import firestore
from google.cloud import pubsub_v1

PARIS_TZ = timezone(timedelta(hours=2))

db = firestore_client.db()
mailer = Mailer()

log = logging.getLogger(__name__)

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
TOPIC_NAME = "email-invitation-to-contribute"

publisher = pubsub_v1.PublisherClient()
full_topic_name = f'projects/{PROJECT_ID}/topics/{TOPIC_NAME}'

PAX_REF_PATH = "reservation_doc_path"


def from_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    log.debug("""This Function was triggered by messageId {} published at {}
       """.format(context.event_id, context.timestamp))
    log.debug(f"event={event}")
    event = Box(event)
    pubsub_message = base64.b64decode(event.data)
    log.debug(f"pubsub_message={pubsub_message}")
    args = pickle.loads(pubsub_message)
    if args:
        deferred_email_invitation_to_contribute(*args)
    else:
        email_invitation_to_contribute()


def defer_email_invitation_to_contribue(pax_ref_path, a_while_ago):
    args = pickle.dumps([pax_ref_path, a_while_ago])
    future = publisher.publish(full_topic_name, base64.b64encode(args))
    return future


def deferred_email_invitation_to_contribute(pax_ref_path, a_while_ago):
    tx = db.transaction()
    deferred_tx_email_invitation_to_contribute(tx, pax_ref_path, a_while_ago)


@firestore.transactional
def deferred_tx_email_invitation_to_contribute(tx, pax_ref_path, a_while_ago):
    log.info(f"pax_ref_path={pax_ref_path} a_while_ago={a_while_ago}")
    pax_ref = db.document(pax_ref_path)

    pax_doc = pax_ref.get()
    assert pax_doc.exists

    pax_reservation_collection_ref = pax_ref.collection('requests')

    reservations_query = common_criteria(
        pax_reservation_collection_ref,
        a_while_ago) \
        .stream(transaction=tx)

    pax = Box(pax_doc.to_dict())
    reservation_docs = list(reservations_query)
    reservations = [Box(reservation_doc.to_dict()) for reservation_doc in reservation_docs]
    log.info(
        f"pax_ref_path={pax_ref_path} a_while_ago={a_while_ago} "
        f"pax.name={pax.name} pax_doc.id={pax_doc.id} len(reservations)={len(reservation_docs)}")

    if not reservations:
        log.warning(f"We came here but to find out there is no reservations to invite for contribution!")
        return

    data = {
        "pax": pax,
        "reservations": reservations,
    }

    rst = render(f"invitation_to_contribute_fr.rst", data)
    title = render(f"invitation_to_contribute_title_fr.txt", data)

    html = to_html(rst)

    mailer.send_mail(pax.name, pax.email, title, html)

    for reservation_doc in reservation_docs:
        tx.update(reservation_doc.reference, {
            "contribution_state": "EMAILED",
        })
    pass


def common_criteria(query, a_while_ago):
    return query \
        .where('state', "==", "CONFIRMED") \
        .where('contribution_state', "==", "START") \
        .where('departure_date', '<', a_while_ago)  \
        .order_by('departure_date', 'ASCENDING')


def email_invitation_to_contribute():
    # TODO: fix timestamp in DB!
    a_while_ago = datetime.now(tz=PARIS_TZ)        \
        .replace(hour=0, minute=0, second=0, microsecond=0)             \
        - timedelta(days=2)

    reservations_query = common_criteria(
        db.collection_group('requests'),
        a_while_ago,
    ).select([]).stream()

    pax_ref_list = set(reservation_doc.reference.parent.parent for reservation_doc in reservations_query)

    futures = (defer_email_invitation_to_contribue(pax_ref.path, a_while_ago) for pax_ref in pax_ref_list)
    for future in futures:
        future.result()
    pass
