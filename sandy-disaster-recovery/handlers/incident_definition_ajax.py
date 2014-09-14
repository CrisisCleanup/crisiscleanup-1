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

class IncidentDefinitionAjax(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    incident_short_name = self.request.get("incident_short_name")
    phase = self.request.get("phase")
    q = incident_definition.IncidentDefinition.all()
    q.filter("short_name =", incident_short_name)
    incident = q.get()
    
    #raise Exception(incident)
    incident_data = {
      "phases_json": incident.phases_json,
      "forms_json": incident.forms_json
    }
    incident_json = json.dumps(incident_data)
    
    self.response.out.write(incident_json)
