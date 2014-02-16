import hashlib
import logging
from google.appengine.ext import deferred
from google.appengine.ext import db
import site_db
import event_db
from models import phase
from models import incident_definition


BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

PERSONAL_INFORMATION_MODULE_ATTRIBUTES = ["name", "request_date", "address", "city", "state", "county", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "rent_or_own", "work_without_resident", "member_of_organization", "first_responder", "older_than_60", "disabled", "special_needs", "priority", "work_type"]


def AddPermissionsSchemaUpdate(cursor=None, num_updated=0):
    single_event_key = None
    ### 
    # To choose an event, uncomment the event short name, and run the last commented line in this block.
    # Make sure you only choose one event_short_name.
    ###
    #event_short_name = "sandy"
    #event_short_name = "test"
    #event_short_name = "hattiesburg"
    #event_short_name = "derechos"
    #event_short_name = "gordon-barto-tornado"
    #event_short_name = "moore"
    #event_short_name = "black_forest"
    #event_short_name = "upstate_flood"
    #event_short_name = "colorado_floods_test"
    #event_short_name = "blue_mountains"
    #event_short_name = "pulaski"
    #event_short_name = "midwest_tornadoes"
    #event_short_name = "ncv_floods"

    #single_event_key = get_single_event_key(event_short_name)
    ###
        
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

    