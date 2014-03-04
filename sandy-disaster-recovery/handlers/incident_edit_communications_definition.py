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
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates/html/default')))

template = jinja_environment.get_template('incident_edit_communications_definition.html')


class IncidentEditCommunicationsDefinition(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    incident_id = self.request.get("id")
    incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))

    form = incident_definition.AdvancedCommunicationsForm(obj=incident)

    data = {
      "form": form,
      "incident_id": incident_id,
    }
    
    self.response.out.write(template.render(data))

  def AuthenticatedPost(self, org, event):
    incident_id = self.request.get("incident_id")
    form = incident_definition.AdvancedCommunicationsForm(self.request.POST)
    
    #form.organization_map_latitude.data = float(form.organization_map_latitude.data)
    #form.organization_map_longitude.data = float(form.organization_map_longitude.data)
    #form.public_map_latitude.data = float(form.public_map_latitude.data)
    #form.public_map_longitude.data = float(form.public_map_longitude.data)
    
    if not form.validate():
      self.response.out.write(template.render(
	{
	  "form": form,
	  "errors": form.errors,
      }))
    else:

      incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))
      incident.notify_contacts = form.notify_contacts.data
      incident.notify_on_new_orgs = form.notify_on_new_orgs.data
      incident.notify_unfinished = form.notify_unfinished.data
      
      incident.put()
      
      self.redirect("/incident_definition?id=" + str(incident_id) + "&show_advanced=yes")
      
      
      
      
      
      
      
      
      
      
      
      

    