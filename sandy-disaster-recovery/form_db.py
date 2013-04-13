#!/usr/bin/env python
#
# Copyright 2013 Andy Gimma
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
import os
import re
import logging
import cache

import jinja2
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import to_dict



ten_minutes = 600


class IncidentForm(db.Model):
    incident = db.ReferenceProperty(required=True)
    form_html = db.TextProperty()
    editable_form_html = db.TextProperty()
    
cache_prefix = IncidentForm.__name__ + "-d:"


def GetCached(incident_form_id):
  return cache.GetCachedById(IncidentForm, ten_minutes, incident_form_id)

def GetAllCached():
    return cache.GetAllCachedBy(IncidentForm, ten_minutes)

def GetAndCache(incident_form_id):
    incident_form = IncidentForm.get_by_id(incident_form_id)
    if incident_form:
        memcache.set(cache_prefix + str(incident_form.key().id()),
        (incident_form, IncidentFormToDict(incident_form)),
        time = cache_time)
        return incident_form
  
def PutAndCache(incident_form, cache_time):
    incident_form.put()
    return memcache.set(cache_prefix + str(incident_form.key().id()),
    (incident_form, IncidentFormToDict(incident_form)),
    time = cache_time)
    
def IncidentFormToDict(incident_form):
  incident_form_dict = to_dict(incident_form)
  incident_form_dict["id"] = incident_form.key().id()
  return incident_form_dict