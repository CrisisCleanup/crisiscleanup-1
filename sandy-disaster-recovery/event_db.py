# System libraries.
import datetime
import hashlib
from google.appengine.ext import db
import logging

# Local libraries.
import site_db

class Event(db.Model):
  name = db.StringProperty(required = True)
  start_date = db.DateProperty()
  num_sites = db.IntegerProperty(default = 0)
  case_label = db.StringProperty(required = True)


def DefaultEventName():
  return "Hurricane Sandy Recovery"

@db.transactional(xg=True)
def AddSiteToEvent(site, event_name, force = False):
  if not len(event_name):
    return False
  event = Event.get_by_key_name(event_name)
  if not site or not event or ((not force) and site.event):
    logging.critical("Could not initialize site: " + site.key().id())
    return False
  site.event = event
  site.case_number = event.case_label + str(event.num_sites)
  event.num_sites += 1
  event.put()
  site.put()
  return True
