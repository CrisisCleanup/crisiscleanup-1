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
import json

# Local libraries.
import base
import key
from models import incident_definition

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates')))
template = jinja_environment.get_template('incident_form_creator.html')

def make_date_object(date_string):
  pass

class IncidentFormCreator(base.RequestHandler):
  def get(self):
    incident_short_name = self.request.get("incident_short_name")
    phase_id = self.request.get("phase_id")
    
    q = incident_definition.IncidentDefinition.all()
    q.filter("short_name =", incident_short_name)
    incident = q.get()
    
    phases_json_string = incident.phases_json
    forms_json_string = incident.forms_json
    #raise Exception(forms_json_string)
    #if forms_json_string == "[]":
    data = {
    "start_array": []
    }
    self.response.out.write(template.render(data))
    return
    
    forms_json_object = json.loads(forms_json_string)
    
    
    raise Exception(forms_json_object)
    form_number = 0
    i = 0
    for form in forms_json_object:
      #if form['phase_id'] == phase_id:
	#phase_number = i
      i += 1
    raise Exception(i)
	
    start_array = json.dumps(phases_json_string)
    raise Exception(start_array)
    data = {
        "start_array": start_array
    }
    self.response.out.write(template.render(data))

  def post(self):
    pass
