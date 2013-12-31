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
from copy import deepcopy

# Local libraries
import base
import site_db
import event_db
from models import phase as phase_db
from models import incident_definition

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class PrivateSiteHandler(base.RequestHandler):      

  def get(self):
    import key

    org, event = key.CheckAuthorization(self.request)
    if not org and event:
      return

    #raise Exception(event.key())
    
    this_key = event.key()
    phase_number = self.request.get("phase_number")
    case_number = self.request.get("case_number")
    phase_id = self.request.get("phase_id")
    try:
      int(phase_number)
    except:
      phase_number = 0
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", this_key)
    inc_def_query = q.get()
    
    #raise Exception(phase_number)
    phases_json = json.loads(inc_def_query.phases_json)
    phase_id = phases_json[int(phase_number)]['phase_id']
    
    event_shortname = self.request.get("shortname")

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

    ids = []
    if inc_def_query.is_version_one_legacy and int(phase_number) == 0:
      gql_string = 'SELECT * FROM Site WHERE status >= :1 and event = :2 and is_legacy_and_first_phase = :3 and case_number = :4'
      q = db.GqlQuery(gql_string, where_string, this_key, True, case_number)
      ids = [key.key().id() for key in q.fetch(1)]
    else: 
      q = Query(model_class = phase_db.Phase)
      #q.filter("event_name =", this_key)
      q.is_keys_only()
      #q.filter("phase_id =", phase_id)
	    

	  
    # TODO
    # Get all entities in a phase.
      ids = [key.site.key().id() for key in q.fetch(PAGE_OFFSET, offset = 0)]

	
    output = json.dumps(
	[s[1] for s in site_db.GetAllCached(event, ids)],
	default=dthandler
    )
    output_array = []
    json_output = json.loads(output)
    #output_copy = deepcopy(json_output)
    remove_from_output_list = ["event_name", "city_metaphone", 'address_metaphone', 'name_metaphone', 'event', 'latitude', 'longitude', 'blurred_latitude', 'blurred_longitude', 'phase_id', 'phone_normalised', 'is_legacy_and_first_phase', 'address_digits', 'id']
    for key in json_output[0]:
      if key in remove_from_output_list:
	pass
	#del output_copy[0][key]
      else:
	output_array.append(key)
    
    final_output = {}
    for key in json_output[0]:
      if key in output_array:
	final_output[key] = json_output[0][key]
	
    #raise Exception(final_output)
    html_string = format_output(final_output)
    #raise Exception(html_string)

    #raise Exception(final_output)
    # TODO
    # format the output, so it fits on a messi
    self.response.out.write(html_string)


def format_output(final_output):
  output_html = ""
  standard_html_output = '<b>Name:</b> ' + final_output['name'] + '<br><b>Date:</b> ' + final_output['request_date'] + '<br><b>Address:</b> ' + final_output['address'] + ' ' + final_output['city'] + ' ' + final_output['state'] + ' ' + final_output['zip_code'] + '<br><b>Status:</b> ' + final_output['status']
  
  standard_list = ['name', 'request_date','address', 'city', 'state', 'zip_code', 'status', 'reported_by', 'claimed_by', 'county', 'work_type', 'case_number']
  
  for key in final_output:
    if key not in standard_list and final_output[key]!= '':
      output_html = output_html + '<br><b>' + str(key) + ':</b> ' + str(final_output[key])
  buttons_html = '<hr><div class="btnbox"><a class="btn " href="/print?case_number=9" target="_blank">Printer Friendly</a><a class="btn " href="#" >Change Status</a><a class="btn " href="#" >Claim</a><a class="btn " id="thi" href="#" >Edit</a></div><script>  $("#thi").click(function() { alert(1); });</script>'
  final_html = standard_html_output + output_html + buttons_html
  return final_html