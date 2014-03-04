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


def show_phases_from_json(phases_json):
    as_json = json.loads(phases_json)
    
    length = len(as_json)
    string = ""
    for obj in as_json:
      def_string = '<p>>' + obj['phase_name'] + ': ' + obj['description'] + '</p>'
      string = string + def_string
    return string

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates/html/default')))

jinja_environment.filters['show_phases_from_json'] = show_phases_from_json

template = jinja_environment.get_template('/incident_list.html')


class IncidentList(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    q = incident_definition.IncidentDefinition.all()
    incidents = q.run()
    
    data = {
      "incidents": incidents,
    }
    self.response.out.write(template.render(data))
    