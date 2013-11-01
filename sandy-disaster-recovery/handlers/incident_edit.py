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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates')))

template = jinja_environment.get_template('/incident_edit.html')


class IncidentEdit(base.RequestHandler):
  def get(self):
    id = self.request.get("id")
    incident = incident_definition.IncidentDefinition.get_by_id(int(id))
    form = incident_definition.IncidentDefinitionForm(obj=incident)

    data = {
      "incident": incident,
      "form": form
    }
    
    self.response.out.write(template.render(data))

  def post(self):
    incident_id = self.request.get("incident_id")
    incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))


    form = incident_definition.IncidentDefinitionForm(self.request.POST, obj=incident)
    del form.incident
    incident_date = form.incident_date.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    form.start_date.data = datetime.strptime(start_date, "%Y-%m-%d").date()
    form.end_date.data = datetime.strptime(end_date, "%Y-%m-%d").date()
    form.incident_date.data = datetime.strptime(incident_date, "%Y-%m-%d").date()
    #form.incident.data = form.incident.data.key()
    #raise Exception(form.incident.data)
    if not form.validate():
      self.response.out.write(template.render(
	{
	  "form": form,
	  "errors": form.errors,
	  "incident": incident
      }))
    else:

      form.populate_obj(incident)
      incident.put()
      return self.redirect("/incident_definition?id=" + incident_id)

    #incident.version = self.request.get("incident_version")
    #incident.full_name = self.request.get("incident_full_name")
    #incident.short_name = self.request.get("incident_short_name")
    #incident.timezone = self.request.get("timezone")
    #incident_date = self.request.get("incident_date")
    #start_date = self.request.get("incident_start_date")
    #end_date = self.request.get("incident_end_date")
    #incident.work_order_prefix = self.request.get("work_order_prefix")
    #incident.centroid_latitude = self.request.get("centroid_latitude")
    #incident.centroid_longitude = self.request.get("centroid_longitude")
    #incident.camera_latitude = self.request.get("camera_latitude")
    #incident.camera_longitude = self.request.get("camera_longitude")
    #incident.developer_mode = bool(self.request.get("developer_mode"))
    #incident.ignore_validation = bool(self.request.get("ignore_validation"))
    
    #incident.local_admin_name = self.request.get("local_admin_name")
    #incident.local_admin_title = self.request.get("local_admin_title")
    #incident.local_admin_organization = self.request.get("local_admin_organization")
    #incident.local_admin_email = self.request.get("local_admin_email")
    #incident.local_admin_cell_phone = self.request.get("local_admin_cell_phone")
    #incident.local_admin_password = self.request.get("local_admin_password") 
  
    #incident.public_map_title = self.request.get("public_map_title")
    #incident.public_map_url = self.request.get("public_map_url")
    #incident.public_map_cluster = bool(self.request.get("public_map_cluster"))
    #incident.public_map_zoom = self.request.get("public_map_zoom")
    
    #incident.internal_map_title = self.request.get("internal_map_title")
    #incident.internal_map_url = self.request.get("internal_map_url")
    #incident.internal_map_cluster = bool(self.request.get("internal_map_cluster"))
    #incident.internal_map_zoom = self.request.get("internal_map_zoom")
  
    ##incident.start_date = datetime.strptime(start_date, "%m-%d-%Y").date()
    ##incident.end_date = datetime.strptime(end_date, "%m-%d-%Y").date()
    ##incident.incident_date_object = datetime.strptime(incident_date, "%m-%d-%Y").date()

    #incident.put()
    
    
