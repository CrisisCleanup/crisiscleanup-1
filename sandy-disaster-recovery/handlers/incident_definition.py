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
import jinja2
import os
import webapp2_extras
from datetime import datetime
from google.appengine.ext import db
import json

# Local libraries.
import base
import key
from models import incident_definition
import event_db
import cache
import random_password
import organization

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates')))
template = jinja_environment.get_template('/incident_definition.html')

read_template = jinja_environment.get_template('/incident_definition_read.html')

CASE_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

def make_date_object(date_string):
  pass

class IncidentDefinition(base.RequestHandler):
  def get(self):
    id = self.request.get("id")
    if id:
      incident_definition_object = incident_definition.IncidentDefinition.get_by_id(int(id))
      phases = json.loads(incident_definition_object.phases_json)
      data = {
	"phases": phases,
	"incident_definition_object": incident_definition_object,
      }
      self.response.out.write(read_template.render(data))
    else:
      form = incident_definition.IncidentDefinitionForm()
      form.local_admin_password.data = random_password.generate_password()
      work_order_prefix = "Set from event_db"
      query_string = "SELECT * FROM Event"
      events_list = db.GqlQuery(query_string)
      count = events_list.count()
      current_date = None
      #form.work_order_prefix.data = CASE_LABELS[count]
      data = {
	"work_order_prefix": CASE_LABELS[count],
	"current_date": current_date,
	"form": form
      }
      self.response.out.write(template.render(data))

  def post(self):
    data = incident_definition.IncidentDefinitionForm(self.request.POST)
    version = data.name.data
    try:
      data.incident_lat.data = float(data.incident_lat.data)
      data.incident_lng.data = float(data.incident_lng.data)
    except:
      pass
    data.local_admin_organization.data = long(data.local_admin_organization.data)

    if not data.validate():
      self.response.out.write(template.render(
	{
	  "form": data,
	  "errors": data.errors,
      }))
    else:
      incident_name = data.name.data
      timezone = data.timezone.data
      location = data.location.data
      
      incident_date = data.incident_date.data
      cleanup_start_date = data.cleanup_start_date.data
      work_order_prefix = data.work_order_prefix.data
      incident_latitude = data.incident_lat.data
      incident_longitude = data.incident_lng.data

      local_admin_name = data.local_admin_name.data
      local_admin_title = data.local_admin_title.data
      local_admin_organization = data.local_admin_organization.data
      local_admin_email = data.local_admin_email.data
      local_admin_cell_phone = data.local_admin_cell_phone.data
      local_admin_password = data.local_admin_password.data
    
      org = organization.Organization.get_by_id(local_admin_organization)
    
    
      incident_date_object = datetime.strptime(incident_date, "%m/%d/%Y").date()
      start_date_object = datetime.strptime(cleanup_start_date, "%m/%d/%Y").date()



      ### TODO
      # Make this happen atomically
      
      incident_short_name = incident_name.lower().replace(" ", "_")
	  
      query_string = "SELECT * FROM Event"
      events_list = db.GqlQuery(query_string)
      count = events_list.count()
      this_event = event_db.Event(name = incident_name,
			  short_name = incident_short_name,
			  case_label = data.work_order_prefix.data,
			)
      ten_minutes = 600
      cache.PutAndCache(this_event, ten_minutes)
      
      # add this version = incident_version
      inc_def = incident_definition.IncidentDefinition(phases_json = "[]", forms_json = "[]", organization_map_latitude = incident_latitude, organization_map_longitude = incident_longitude, public_map_latitude = incident_latitude, public_map_longitude = incident_longitude, location = location, name = incident_name, short_name = incident_short_name, timezone = timezone, incident_date = incident_date_object, cleanup_start_date = start_date_object, work_order_prefix = work_order_prefix, incident_lat = incident_latitude, incident_lng = incident_longitude, local_admin_name = local_admin_name, local_admin_title = local_admin_title, local_admin_organization = org.key(), local_admin_email = local_admin_email, local_admin_cell_phone = local_admin_cell_phone, local_admin_password = local_admin_password, incident = this_event.key())
      inc_def.put()

      
      self.redirect("/incident_definition?id=" + str(inc_def.key().id()))

def get_phases_from_json(phases_json):
  pass