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

# Local libraries.
import base
import key
from models import incident_definition
import json

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates')))
template = jinja_environment.get_template('incident_form_creator.html')

def make_date_object(date_string):
  pass

class IncidentFormCreator(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    incidents = incident_definition.IncidentDefinition.all()
    inc_array = []
    for inc in incidents:
      forms_json = json.loads(inc.forms_json)
      for form in forms_json:
	inc_dict = {
	  form[0]['incident_short_name']: form[0]['phase_name']
	}
	inc_array.append(inc_dict)
    data = {
        "incidents": incidents,
        "inc_array": create_radio_group(inc_array)
    }
    self.response.out.write(template.render(data))

  def AuthenticatedPost(self, org, event):
    pass

def create_radio_group(inc_array):
  radio_html = '<div class="clone"><input type="radio" name="clone_group" class="clone_class" id="empty" value="empty">None</div>'
  for inc in inc_array:
    for key in inc.keys():
      new_html = '<div class="clone"><input type="radio" name="clone_group" class="clone_class" id="' + key + '" value="' + inc[key] + '">'  + key + ' | Phase:' + inc[key] + '</div>'
      radio_html = radio_html + new_html
  return radio_html