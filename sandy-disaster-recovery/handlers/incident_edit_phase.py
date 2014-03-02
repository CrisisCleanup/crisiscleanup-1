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

template = jinja_environment.get_template('/incident_edit_phase.html')


class IncidentEditPhase(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    incident_short_name = self.request.get("incident_short_name")
    phase_id = self.request.get("phase_id")
    q = incident_definition.IncidentDefinition.all()
    q.filter("short_name =", incident_short_name)
    incident = q.get()
    
    phases_json = json.loads(incident.phases_json)
    this_phase = None
    for phase in phases_json:
      if phase['phase_id'] == phase_id:
	this_phase = phase
    #raise Exception(this_phase)
    form = incident_definition.IncidentPhaseForm(phase_name = this_phase['phase_name'], description=this_phase['description'])
    data = {
      "incident": incident,
      "form": form,
      "this_phase": this_phase
    }
    
    self.response.out.write(template.render(data))
    
    
  def AuthenticatedPost(self, org, event):
    incident_id = self.request.get("incident_id")
    phase_id = self.request.get("phase_id")
    phase_name = self.request.get("phase_name")
    description = self.request.get("description")
    
    form = incident_definition.IncidentPhaseForm(self.request.POST)
    incident = incident_definition.IncidentDefinition.get_by_id(int(incident_id))
    
    phases_json = json.loads(incident.phases_json)

    i = 0
    phase_number = 0
    for phase in phases_json:
      if phase['phase_id'] == phase_id:
	phase_number = i
      i += 1

    if form.validate():      
      phase_short_name = phase_name.lower()
      phase_short_name = phase_short_name.replace(" ", "_")
      
      

      edited_phase_obj = {
	"phase_name": phase_name,
	"phase_id": phase_id,
	"incident_short_name": incident.short_name,
	"description": description,
	"phase_short_name": phase_short_name
      }
      
      phases_json[phase_number] = edited_phase_obj
      incident.phases_json = json.dumps(phases_json)
      incident.put()
      self.redirect("/incident_definition?id=" + incident_id)
      return
    else:
      data = {
	"incident": incident,
	"form": form,
	"this_phase": phases_json[phase_number],
	"errors": form.errors
      }
      
      self.response.out.write(template.render(data))
      return