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
## System libraries.
import logging
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
from google.appengine.api import memcache

## Local libraries
import cache

class IncidentDefinition(db.Model):
  version = db.StringProperty(required=True)
  full_name = db.StringProperty(required=True)
  short_name = db.StringProperty(required=True)
  timezone = db.StringProperty(required=True)
  incident_date = db.DateProperty(required=True)
  start_date = db.DateProperty(required=True)
  end_date = db.DateProperty(required=True)
  work_order_prefix = db.StringProperty(required=True)
  centroid_lat = db.StringProperty(required=True)
  centroid_lng = db.StringProperty(required=True)
  incident_form_json = db.TextProperty()
  