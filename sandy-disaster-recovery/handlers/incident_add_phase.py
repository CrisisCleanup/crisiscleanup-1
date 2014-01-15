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

template = jinja_environment.get_template('/incident_add_phase.html')


class IncidentAddPhase(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    _id = self.request.get("id")
    incident_definition_object = incident_definition.IncidentDefinition.get_by_id(int(_id))
    phases_empty_boolean = False
    if incident_definition_object.phases_json:
      phases_empty_boolean = True
    form = incident_definition.IncidentPhaseForm()
    data = {
      "incident_definition_object": incident_definition_object,
      "form": form,
      "phases_empty": phases_empty_boolean,
    }
    self.response.out.write(template.render(data))
  def AuthenticatedPost(self, org, event):
    incident_id = self.request.get("incident_id")
    phase_name = self.request.get("phase_name")
    description = self.request.get("description")
    add_phase = self.request.get("add_phase")
    incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))
    form = incident_definition.IncidentPhaseForm(self.request.POST)
    
    if form.validate():    
      phase_short_name = phase_name.lower()
      phase_short_name = phase_short_name.replace(" ", "_")
      phase_data = {
      "phase_name": phase_name,
      "description": description,
      "phase_short_name": phase_short_name,
      "phase_id": os.urandom(16).encode("hex"),
      "incident_short_name": incident.short_name
      }
      
      phase_array = []
      
      phase_array.append(phase_data)
      
      phases_json = json.dumps(phase_array)
      
      #if not add_phase:
	#incident.phases_json = phases_json
	#incident.put()
      #else:
      phases_array = incident.phases_json
      arr = json.loads(phases_array)
      arr.append(phase_data)
      incident.phases_json = json.dumps(arr)
      
      incident.put()
      
      self.redirect("incident_form_creator?incident_short_name=" + str(event.short_name) + "&phase_id=" + str(phase_short_name))
    else:
      data = {
	"incident_definition_object": incident,
	"form": form,
	"errors": form.errors
      }
      self.response.out.write(template.render(data))