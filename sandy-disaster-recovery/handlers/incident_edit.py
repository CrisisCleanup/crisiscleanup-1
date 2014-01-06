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
import organization

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates')))

template = jinja_environment.get_template('/incident_edit.html')


class IncidentEdit(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    id = self.request.get("id")
    incident = incident_definition.IncidentDefinition.get_by_id(int(id))
    form = incident_definition.IncidentDefinitionForm(obj=incident)

    data = {
      "incident": incident,
      "form": form
    }
    
    self.response.out.write(template.render(data))

  def AuthenticatedPost(self, org, event):
    incident_id = self.request.get("incident_id")
    incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))


    form = incident_definition.IncidentDefinitionForm(self.request.POST, obj=incident)
    del form.incident

    #form.incident.data = incident_id
    #raise Exception(form.incident.data)
    #form.incident.data = form.incident.data.key()
    try:
      form.incident_lat.data = float(form.incident_lat.data)
      form.incident_lng.data = float(form.incident_lng.data)
    except:
      pass
    form.local_admin_organization.data = long(form.local_admin_organization.data)
    if not form.validate():
      self.response.out.write(template.render(
	{
	  "form": form,
	  "errors": form.errors,
	  "incident": incident
      }))
    else:
      form.incident_date.data = datetime.strptime(form.incident_date.data, "%Y-%m-%d").date()
      form.cleanup_start_date.data = datetime.strptime(form.cleanup_start_date.data, "%Y-%m-%d").date()
      form.local_admin_organization.data = organization.Organization.get_by_id(form.local_admin_organization.data).key()
      
      event = incident.incident
      event_changed = False
      short_name = form.name.data.lower().replace(" ", "_")
      if event.name != form.name.data:
	event_changed = True
	event.name = form.name.data
	event.short_name = short_name
      if event.case_label != form.work_order_prefix.data:
	event_changed = True
	event.case_label = form.work_order_prefix.data
      if event_changed:
	event.put()

      phases_json = incident.phases_json
      forms_json = incident.forms_json
      
      org_lat = incident.organization_map_latitude
      org_lng = incident.organization_map_longitude
      
      pub_lat = incident.public_map_latitude
      pub_lng = incident.public_map_longitude
      
      original_lat = incident.incident_lat
      original_lng = incident.incident_lng
      
      form.populate_obj(incident)
      incident.phases_json = phases_json
      incident.forms_json = forms_json
      incident.short_name = short_name

      if form.incident_lat.data != original_lat:
	incident.organization_map_latitude = form.incident_lat.data
	incident.public_map_latitude = form.incident_lat.data
      if form.incident_lng.data != original_lng:
	incident.organization_map_longitude = form.incident_lng.data
	incident.public_map_longitude = form.incident_lng.data

      incident.put()
      return self.redirect("/incident_definition?id=" + incident_id)


    
