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


def AddPhasesSchemaUpdate(cursor=None, num_updated=0):
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
    phase_to_put = []
    inc_def_query_dict = {}
    phase_id_dict = {}
    for p in query.fetch(limit=BATCH_SIZE):
        site_dict = site_db.SiteToDict(p)
        phase_dict = {}

	inc_def_query_key, inc_def_query_dict = find_inc_def_query_key(p.event.key(), inc_def_query_dict)
	phase_id_hash, phase_id_dict = find_phase_id_hash(p.event.key(), phase_id_dict)
	phase_obj = phase.Phase(incident = p.key(), site = p.key(), phase_id = "123")
        for k in site_dict:
	  if k == "work_type":
	    setattr(phase_obj, k, str(v))
	  if k not in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	    v = site_dict[k]
	    setattr(p, k, None)
	    setattr(phase_obj, k, str(v))
	
	phase_to_put.append(phase_obj)
	to_put.append(p)

    ## Check to_put and phase_to_put
    ## raise Exception so it doesn't go further
    #raise Exception(len(to_put))
    if to_put and phase_to_put:
        db.put(to_put)
        db.put(phase_to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)
	
def find_inc_def_query_key(incident_key, inc_def_query_dict):
  if incident_key in inc_def_query_dict:
    return inc_def_query_dict[str(incident_key)], inc_def_query_dict
  else:
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", incident_key)
    inc_def_query = q.get()
    inc_def_query_dict[str(incident_key)] = str(inc_def_query.key())
    return inc_def_query_dict[str(incident_key)], inc_def_query_dict
  
def find_phase_id_hash(incident_key, phase_id_dict):
  if incident_key in phase_id_dict:
    return phase_id_dict[incident_key], phase_id_dict
  else:
    m = hashlib.md5()
    m.update(str(incident_key))
    h = m.hexdigest()
    phase_id_dict[str(incident_key)] = h
    return h, phase_id_dict
    
def get_single_event_key(event_short_name):
    q = db.Query(event_db.Event)
    q.filter("short_name =", event_short_name)
    event = q.get()
    if event:
      return event.key()
    else:
      raise Exception("That incident does not exist in this database.")
      return None
    