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


class IncidentCSV(db.Model):
    incident = db.ReferenceProperty(required=True)
    incident_csv = db.StringListProperty()
    
cache_prefix = IncidentCSV.__name__ + "-d:"


def GetCached(incident_csv_id):
  return cache.GetCachedById(IncidentCSV, ten_minutes, incident_csv_id)

def GetAllCached():
    return cache.GetAllCachedBy(IncidentCSV, ten_minutes)

def GetAndCache(incident_csv_id):
    incident_csv = IncidentCSV.get_by_id(incident_csv_id)
    if incident_csv:
        memcache.set(cache_prefix + str(incident_csv.key().id()),
        (incident_csv, IncidentCSVToDict(incident_csv)),
        time = cache_time)
        return incident_csv
  
def PutAndCache(incident_csv, cache_time):
    incident_csv.put()
    return memcache.set(cache_prefix + str(incident_csv.key().id()),
    (incident_csv, IncidentCSVToDict(incident_csv)),
    time = cache_time)
    
def IncidentCSVToDict(incident_csv):
  incident_csv_dict = to_dict(incident_csv)
  incident_csv_dict["id"] = incident_csv.key().id()
  return incident_csv_dict