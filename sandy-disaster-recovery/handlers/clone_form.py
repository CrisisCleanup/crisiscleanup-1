#!/usr/bin/env python
#
# Copyright 2014 Andy Gimma
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
from google.appengine.ext import db
import json
import time
import hashlib

# Local libraries.
import base
import key
from models import incident_definition
import event_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates/html/default')))

template = jinja_environment.get_template('/clone_form.html')

class CloneForm(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    #inc_def_query = incident_definition.IncidentDefinition.get_by_id(int(self.request.get("incident_id")))
    incident_id = self.request.get("incident_id")
    q = event_db.Event.all()
    events = q.fetch(100)
    
    data = {
      "events": events,
      "incident_id": incident_id,
    }
    self.response.out.write(template.render(data))
  def AuthenticatedPost(self, org, event):
    cloned_incident_id = self.request.get("incident_group")
    this_incident_id = self.request.get("incident_id")
    clone_by_id(cloned_incident_id, this_incident_id)
    self.redirect("/incident_definition?id=" + this_incident_id)
    
    
    
def clone_by_id(old_id, new_id):
  old_int = int(old_id)
  new_int = int(new_id)
  old_event = event_db.Event.get_by_id(old_int)
  
  # get old inc_def
  
  q = incident_definition.IncidentDefinition.all()
  q.filter("incident =", old_event)
  old_inc_def = q.get()
  

  new_inc_def = incident_definition.IncidentDefinition.get_by_id(new_int)
  new_phases_def = json.loads(old_inc_def.phases_json)
  new_forms_def = json.loads(old_inc_def.forms_json)
  
  time_now = time.time()

  for phase in new_phases_def:
    # create hex
    phase["phase_id"] = create_hex_by_phase_name_and_time(phase["phase_name"], time_now)
    
  for form in new_forms_def:
    #hash_ = create_hex_by_phase_name_and_time(phase["phase_name"], time_now)
    #raise Exception(hash_)
    form[0]["phase_id"] = create_hex_by_phase_name_and_time(phase["phase_name"], time_now)
    
      
  new_inc_def.phases_json = json.dumps(new_phases_def)
  new_inc_def.forms_json = json.dumps(new_forms_def)
  new_inc_def.put()
        
  
 
 
def create_hex_by_phase_name_and_time(phase_name, time_now):
  salt = "234adfsjkl235"
  m = hashlib.md5(salt)
  m.update(str(phase_name))
  m.update(str(time_now))
  new_hash = m.hexdigest()
  return new_hash

  
  