# System libraries.
import datetime
import hashlib
from google.appengine.ext import db
import logging

from google.appengine.api import memcache

# Local libraries.
import cache

class Event(db.Model):
  name = db.StringProperty(required = True)
  start_date = db.DateProperty()
  num_sites = db.IntegerProperty(default = 0)
  case_label = db.StringProperty(required = True)

import site_db


def DefaultEventName():
  return "Hurricane Sandy Recovery"

@db.transactional(xg=True)
def AddSiteToEvent(site, event_id, force = False):
  event = Event.get_by_id(event_id)
  if not site or not event or ((not force) and site.event):
    logging.critical("Could not initialize site: " + str(site.key().id()))
    return False
  site.event = event
  site.case_number = event.case_label + str(event.num_sites)
  event.num_sites += 1
  event.put()
  site.put()
  return True

ten_minutes = 600
def GetDefaultEvent():
  cache_key = 'Event:default'
  event = memcache.get(cache_key)
  if event:
    return event
  event_q = Event.gql("WHERE name = :name", name = DefaultEventName())
  for e in event_q:
    memcache.set(cache_key, e, ten_minutes)
    return e
  return None

def GetEventFromParam(event_id_param):
  try:
    event_id = int(event_id_param)
    event = GetCached(event_id)
  except:
    event = GetDefaultEvent()
  return event

def GetCached(event_id):
  return cache.GetCachedById(Event, ten_minutes, event_id)

def GetAllCached():
  return cache.GetAllCachedBy(Event, ten_minutes)

def GetAndCache(event_id):
  return cache.GetAndCache(Event, ten_minutes, event_id)
