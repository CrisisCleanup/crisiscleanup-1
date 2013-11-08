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


class IncidentSaveForm(base.RequestHandler):
  def post(self):
    id_array = None
    form_json_array = self.request.get("form_json_array")
    new_array = json.loads(form_json_array)
    q = incident_definition.IncidentDefinition.all()
    for array in new_array:
      if "incident_short_name" in array:
	id_array = array
    q.filter("short_name =", id_array['incident_short_name'])
    incident = q.get()
    
    forms_array = []
    forms_array.append(new_array)
    
    pre_existing_forms_json = incident.forms_json
    pefj = json.loads(pre_existing_forms_json)
    
    # check if this form (with phase id) is already there, if so, replace it, if not, add it
    
    
    pefj.append(new_array)
    
    incident.forms_json = json.dumps(pefj)
    incident.put()
    
    