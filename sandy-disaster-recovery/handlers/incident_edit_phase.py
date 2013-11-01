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


class IncidentEditPhase(base.RequestHandler):
  def get(self):
    incident_short_name = self.request.get("incident")
    q = incident_definition.IncidentDefinition.all()
    q.filter("short_name =", incident_short_name)
    incident = q.get()
    
    data = {
      "incident": incident,
    }
    
    self.response.out.write(template.render(data))
    
    
  def post(self):
    if self.request.get("phase1"):
      pass
      # get all and add to json
    if self.request.get("phase2"):
      pass
      # get all and add to json
    if self.request.get("phase3"):
      pass
      # get all and add to json
    if self.request.get("phase4"):
      pass
      # get all and add to json
    if self.request.get("phase5"):
      pass
      # get all and add to json
    if self.request.get("phase6"):
      pass
      # get all and add to json