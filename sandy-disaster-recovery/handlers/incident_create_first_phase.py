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

def make_date_object(date_string):
  pass

class IncidentCreateFirstPhase(base.RequestHandler):
  def post(self):
    incident_short_name = self.request.get("incident_short_name")
    phase_name = self.request.get("phase_name")
    phase_definition = self.request.get("phase_definition")
    phase_position = self.request.get("phase_position")
    add_phase = self.request.get("add_phase")
    q = incident_definition.IncidentDefinition.all()
    q.filter("short_name =", incident_short_name)
    incident = q.get()
    
    phase_short_name = phase_name.lower()
    phase_short_name = phase_short_name.replace(" ", "_")
    phase_data = {
     "phase_name": phase_name,
     "phase_definition": phase_definition,
     "phase_position": phase_position,
     "phase_short_name": phase_short_name,
     "phase_id": os.urandom(16).encode("hex"),
     "incident_short_name": incident_short_name
    }
    
    phase_array = []
    
    phase_array.append(phase_data)
    
    phases_json = json.dumps(phase_array)
    if not add_phase:
      incident.phases_json = phases_json
      incident.put()
    else:
      phases_array = incident.phases_json
      arr = json.loads(phases_array)
      arr.append(phase_data)
      incident.phases_json = json.dumps(arr)
      incident.put()
    
    self.redirect("incident_form_creator")
