import hashlib
import logging
from google.appengine.ext import deferred
from google.appengine.ext import db
import site_db
import event_db
from models import incident_definition


BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

PERSONAL_INFORMATION_MODULE_ATTRIBUTES = ["name", "request_date", "address", "city", "state", "county", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "rent_or_own", "work_without_resident", "member_of_organization", "first_responder", "older_than_60", "disabled", "special_needs", "priority", "work_type"]


def AddPermissionsSchemaUpdate(cursor=None, num_updated=0):
    single_event_key = None
        
    query = site_db.Site.all()
    if single_event_key:
      query.filter("event =", single_event_key)

    if cursor:
        query.with_cursor(cursor)

    to_put = []

    for p in query.fetch(limit=BATCH_SIZE):
        p.permission="Full Access"
        
    if to_put and phase_to_put:
        db.put(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)

    