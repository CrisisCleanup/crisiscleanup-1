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
  # TODO

  # is the next one necessary?
  #full_definition_json = db.TextProperty(required=True, default="{}")
  # should we make the next two attributes lists, rather than just json?
  phases_json = db.TextProperty(required=True, default="{}")
  # name, definition, order_number, incident reference, incident name
  forms_json = db.TextProperty(required=True, default="{}")
  # name, incident reference, incident name, attributes json
  
  # removing versions until we know what will likely be inherited
  
  #version = db.StringProperty(required=True)
  incident = db.ReferenceProperty(required=True)
  # ensure unique
  full_name = db.StringProperty(required=True)
  # ensure unique
  short_name = db.StringProperty(required=True)
  # ensure unique
  timezone = db.StringProperty(required=True)
  incident_date = db.DateProperty(required=True)
  start_date = db.DateProperty(required=True)
  end_date = db.DateProperty(required=True)
  work_order_prefix = db.StringProperty(required=True)
  centroid_lat = db.StringProperty(required=True)
  centroid_lng = db.StringProperty(required=True)
  camera_lat = db.StringProperty()
  camera_lng = db.StringProperty()
  ignore_validation = db.BooleanProperty()
  developer_mode = db.BooleanProperty()
  
  local_admin_name = db.StringProperty()
  local_admin_title = db.StringProperty()
  local_admin_organization = db.StringProperty()
  local_admin_email = db.StringProperty()
  local_admin_cell_phone = db.StringProperty()
  local_admin_password = db.StringProperty()

  public_map_title = db.StringProperty()
  public_map_url = db.StringProperty()
  public_map_cluster = db.BooleanProperty()
  public_map_zoom = db.StringProperty()
  
  internal_map_title = db.StringProperty()
  internal_map_url = db.StringProperty()
  internal_map_cluster = db.BooleanProperty()
  internal_map_zoom = db.StringProperty()