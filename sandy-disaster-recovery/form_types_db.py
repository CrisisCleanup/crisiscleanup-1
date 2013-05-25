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


class FormTypes(db.Model):
    incident = db.ReferenceProperty(required=True)
    properties_json = db.TextProperty()
    
cache_prefix = FormTypes.__name__ + "-d:"


def GetCached(form_types_id):
  return cache.GetCachedById(FormTypes, ten_minutes, form_types_id)

def GetAllCached():
    return cache.GetAllCachedBy(FormTypes, ten_minutes)

def GetAndCache(form_types_id):
    form_types = FormTypes.get_by_id(form_types_id)
    if form_types:
        memcache.set(cache_prefix + str(form_types.key().id()),
        (form_types, FormTypesToDict(form_types)),
        time = cache_time)
        return form_types
  
def PutAndCache(form_types, cache_time):
    form_types.put()
    return memcache.set(cache_prefix + str(form_types.key().id()),
    (form_types, FormTypesToDict(form_types)),
    time = cache_time)
    
def FormTypesToDict(form_types):
  form_types_dict = to_dict(form_types)
  form_types_dict["id"] = form_types.key().id()
  return form_types_dict