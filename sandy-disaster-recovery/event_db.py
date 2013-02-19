#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# System libraries.
import datetime
import hashlib
from google.appengine.ext import db
import logging

from google.appengine.api import memcache
from wtforms.ext.appengine.db import model_form


# Local libraries.
import cache
import wtforms
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField


class Event(db.Model):
  name = db.StringProperty(required = True)
  short_name = db.StringProperty()
  created_date = db.DateProperty(auto_now_add=True)
  start_date = db.DateProperty(auto_now_add=True)
  end_date = db.DateProperty()
  num_sites = db.IntegerProperty(default = 0)
  case_label = db.StringProperty()
  counties = db.StringListProperty()
  latitudes = db.ListProperty(float)
  longitudes = db.ListProperty(float)
  reminder_days = db.IntegerProperty(default=15)
  reminder_contents = db.TextProperty()

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
  cache.PutAndCache(event, ten_minutes)
  
  site.put()
  return True

ten_minutes = 600
@db.transactional(xg=True)
def SetCountiesForEvent(event_id, counties):
  event = Event.get_by_id(event_id)
  event.counties = [county for county in counties]
  event.latitudes = []
  event.longitudes = []
  cache.PutAndCache(event, ten_minutes)
  return True

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

def ReduceNumberOfSitesFromEvent(event_id):
  event = Event.get_by_id(event_id)
  event.num_sites -= 1
  cache.PutAndCache(event, ten_minutes)

class NewEventForm(model_form(Event)):
    name = TextField('Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    short_name = TextField('Short Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])