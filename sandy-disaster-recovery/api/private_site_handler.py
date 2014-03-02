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
import hashlib
import time


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
  
  def post(self):
    import key

    org, event = key.CheckAuthorization(self.request)
    if not org and event:
      return
    
    claim = self.request.get("claim")
    case_number = self.request.get("case_number")
    phase_id = self.request.get("phase_id")
    if claim == "Claim":
      
      q = site_db.Site.all()
      q.filter("case_number = ", case_number)
      site = q.get()
      site.claim_for_org = "y"
      site.claimed_by = org.key()
      try:
	site_db.PutAndCache(site)
	self.response.out.write("<h4>Claimed for " + org.name + "</h4>")
      except:
	self.response.out.write('<h4 style="text-color:red;">Claim Failed</h4>')
    elif claim == "Unclaim":
            
      q = site_db.Site.all()
      q.filter("case_number = ", case_number)
      site = q.get()
      site.claim_for_org = "n"
      site.claimed_by = None
      try:
	site_db.PutAndCache(site)
	self.response.out.write("<h4>Unclaimed by " + org.name + "</h4>")
      except:
	self.response.out.write('<h4 style="text-color:red;">Unclaim Failed</h4>')
      
    else:
      work_type = self.request.get("work_type")
      
      q = site_db.Site.all()
      q.filter("case_number = ", case_number)
      site = q.get()
      #raise Exception(site)
      site.work_type = work_type
      #raise Exception(site.work_type)
      try:
	site_db.PutAndCache(site)
	self.response.out.write("<h4>Update Successful</h4>")
      except:
	self.response.out.write('<h4 style="text-color:red;">Update Failed</h4>')

      
   

  def get(self):
    import key

    org, event = key.CheckAuthorization(self.request)
    if not org and event:
      return

    if self.request.get("get_phase_form"):
      incident_short_name = self.request.get("incident_short_name")
      phase_name = self.request.get("phase_name")

      
      if incident_short_name == "empty":
	self.response.out.write("[]")
	return
      
      q = db.Query(event_db.Event)
      q.filter("short_name =", incident_short_name)
      event_query = q.get()
      
      q = db.Query(incident_definition.IncidentDefinition)
      q.filter = ("incident = ", event_query.key())
      inc_def_query = q.get()
      
      new_phase_id = getPhaseId(phase_name, inc_def_query)
      
      forms_json = json.loads(inc_def_query.forms_json)
      return_form = None
      for form in forms_json:
	if form[0]['phase_name'] == phase_name:
	  form[0]['phase_id'] = new_phase_id
	  return_form = form
	  return_form[0]['phase_id'] = new_phase_id
      self.response.out.write(json.dumps(return_form))
      return
	  
      
    #raise Exception(event.key())
    
    this_key = event.key()
    phase_number = self.request.get("phase_number")
    case_number = self.request.get("case_number")
    
    edit = self.request.get("edit")
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
    
    s = Query(model_class = site_db.Site)
    s.filter("case_number =", case_number)
    this_site = s.get()

    q = Query(model_class = phase_db.Phase)
    q.filter("site =", this_site)
    q.is_keys_only()
    #q.filter("phase_id =", phase_id)
	  

	
  # TODO
  # Get all entities in a phase.
    ids = [key.site.key().id() for key in q.fetch(PAGE_OFFSET, offset = 0)]
    #raise Exception(ids)

    #raise Exception(ids)
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
    html_string = format_output(final_output, case_number, phase_number, phase_id, ids[0], inc_def_query)
    #raise Exception(html_string)

    #raise Exception(final_output)
    # TODO
    # format the output, so it fits on a messi
    #raise Exception(inc_def_query.forms_json)
    # get correct form by getPhaseId
    # loop through, if phase_id matches, get thing
    #forms = json.loads(inc_def_query.forms_json)

    #work_types = []
    #for form_obj in forms[phase_number]:
      #if "_id" in form_obj and form_obj["_id"] == "work_type":
	#for key, value in form_obj.iteritems():
	  #if "select_option" in key:
	    #work_types.append(value)
    ## create select, with correct default
    ## add to format_output 
    #work_select_string = '<select id="work_type">'
    #for work in work_types:
      #work_select_string = work_select_string + '<option value="' + work + '">' + work + '</option>'
    #work_select_string = work_select_string + "</select>"
    #raise Exception(work_select_string)
      	    
      
    self.response.out.write(html_string)


def format_output(final_output, case_number, phase_number, phase_id, site_id, inc_def_query):
  case_number = str(case_number)
  phase_number = str(phase_number)
  phase_id = str(phase_id)
  output_html = ""
  work_type_script = '<script>$("#work_type_select").change(  function() { var case_number = "' + case_number + '"; var phase_id="' + phase_id + '"; value = $("#work_type_select").val(); $.post( "api/private_site_handler",{ case_number: case_number, phase_id: phase_id, work_type: value}, function( data ) { $( ".messi-content" ).prepend( data ); }); });</script>'
  
  claim_script = ' <script>$("#claim_btn").click(  function() { var claim_value = $("#claim_btn").html(); if(typeof claim_value === "undefined") { claim_value = "Unclaim"; } ; var case_number = "' + case_number + '"; var phase_id="' + phase_id + '"; $.post( "api/private_site_handler",{ case_number: case_number, phase_id: phase_id, claim: claim_value}, function( data ) { $( ".messi-content" ).append( data ); $("#claim_btn").html("Unclaim"); $("#claim_btn").attr("id","unclaim_btn");  }); });</script>'
  
  unclaim_script = ' <script>$("#unclaim_btn").click(  function() { var case_number = "' + case_number + '"; var phase_id="' + phase_id + '"; $.post( "api/private_site_handler",{ case_number: case_number, phase_id: phase_id, unclaim: "true"}, function( data ) { $( ".messi-content" ).append( data ); $("#claim_btn").html("Claim"); $("#claim_btn").attr("id","claim_btn");  }); });</script>'
  
  edit_script = ' <script>$("#messi_edit").click(  function() { show_edit(); });</script>'
  
  standard_html_output = edit_script + work_type_script + claim_script + '<div class="messi_python"><b>Name:</b> ' + final_output['name'] + '<br><b>Date:</b> ' + final_output['request_date'] + '<br><b>Address:</b> ' + final_output['address'] + ' ' + final_output['city'] + ' ' + final_output['state'] + ' ' + final_output['zip_code'] + '<br><b>Status:</b> '
  
  forms = json.loads(inc_def_query.forms_json)

  work_types = []
  #raise Exception(phase_number)
  phase_number_int = None
  try:
    phase_number_int = int(phase_number)
  except:
    phase_number_int = 0
  for form_obj in forms[phase_number_int]:
    if "_id" in form_obj and form_obj["_id"] == "work_type":
      for key, value in form_obj.iteritems():
	if "select_option" in key:
	  work_types.append(value)
  # create select, with correct default
  # add to format_output 
  work_select_string = '<select id="work_type_select">'
  for work in work_types:
    add_selected = 'selected="selected"'
    if work == final_output["work_type"]:
      work_select_string = work_select_string + '<option ' + add_selected + ' value="' + work + '">' + work + '</option>'
    else:
      work_select_string = work_select_string + '<option value="' + work + '">' + work + '</option>'
  work_select_string = work_select_string + "</select><br>"
  
  standard_html_output = standard_html_output + work_select_string

  standard_list = ['name', 'request_date','address', 'city', 'state', 'zip_code', 'status', 'reported_by', 'claimed_by', 'county', 'work_type', 'case_number']
  
  edit_url = '/edit?id=' + str(site_id) + '&phase=' + phase_number
  
  
  for key in final_output:
    if key not in standard_list and final_output[key]!= '':
      output_html = output_html + ' <b>' + str(key) + ':</b> ' + str(final_output[key])
  buttons_html = '</div><hr><div class="btnbox"><a class="btn " href="/print?case_number=' + case_number + '&phase_number=' + phase_number + '&phase_id=' + phase_id +'" target="_blank">Printer Friendly</a><a class="btn " id="claim_btn" href="#" >Claim</a><a class="btn " id="messi_edit">Edit</a></div>'
  final_html = standard_html_output + output_html + buttons_html
  return final_html


def getPhaseId(phase_name, inc_def_query):
  phase_id = None
  phases_json = json.loads(inc_def_query.phases_json)
  for form in phases_json:
    #raise Exception(form)

    if form['phase_name'] == phase_name:
      phase_id = form['phase_id']
  return phase_id
  