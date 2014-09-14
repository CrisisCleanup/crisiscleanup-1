#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
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
import datetime
import jinja2
import json
import os
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import Query
from collections import OrderedDict

# Local libraries
import base
import site_db
import event_db
from models import incident_definition
from helpers import phase_helpers

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class PrivateMapHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    phase_number = self.request.get("phase_number")
    if not phase_number:
      phase_number = 0
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    
    
    phases_json = json.loads(inc_def_query.phases_json)
    phase_id = phases_json[int(phase_number)]['phase_id']
    forms_json_obj = json.loads(inc_def_query.forms_json)

    phase_name = phase_helpers.get_phase_name(forms_json_obj, phase_number)
    event_shortname = self.request.get("shortname")
    page = self.request.get("page")
    page_int = int(page)
    phase = self.request.get("phase")
    
    # TODO
    # Get phase_id from phase
    # after this, should work perfectly

    if event_shortname == None:
      event_shortname = "sandy"
    event = None
    events = event_db.GetAllCached()
    for e in events:
      if e.short_name == event_shortname:
	event = e

      
    ids = []
    where_string = "Open"
    q = None
    this_offset = page_int * PAGE_OFFSET

    ids = []

    q = Query(model_class = site_db.Site)
    q.filter("event =", event.key())
    q.filter("open_phases_list =", phase_name.lower())
    q.is_keys_only()
    query = q.fetch(PAGE_OFFSET, offset=this_offset)
    #raise Exception(query)
    ids = [site.key().id() for site in query]
    

    # TODO
    # Get all entities in a phase.
    # ids = [key.site.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]

	
    output = json.dumps(
	[s[1] for s in site_db.GetAllCached(event, ids)],
	default=dthandler
    )
    self.response.out.write(output)


#def get_phase_name(form_json, phase_number):
  #phase_number = int(phase_number)
  #i = 0
  #phase_name = ""
  #for obj in form_json:
    #if phase_number == i:
      #for data in obj:
	#if 'phase_name' in data:
	  #phase_name = data["phase_name"]
    #i += 1
  #return phase_name
