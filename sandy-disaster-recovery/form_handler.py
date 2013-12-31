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
import cgi
import jinja2
import logging
import os
import urllib2
import wtforms.validators
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
import json
from datetime import datetime



# Local libraries.
import base
import event_db
import site_db
import site_util
import form_db
import site_db

import random

from models import incident_definition
from helpers import populate_incident_form
import wtforms.ext.dateutil.fields
import wtforms.fields
from wtforms import Form, BooleanField, TextField, TextAreaField, validators, PasswordField, ValidationError, RadioField, SelectField
from models import phase

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
menubox_template = jinja_environment.get_template('_menubox.html')
HATTIESBURG_SHORT_NAME = "hattiesburg"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"


PERSONAL_INFORMATION_MODULE_ATTRIBUTES = ["name", "request_date", "address", "city", "state", "county", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "rent_or_own", "work_without_resident", "member_of_organization", "first_responder", "older_than_60", "disabled", "special_needs", "priority"]

class IncidentForm(site_db.Site):
  pass

class FormHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    
    phase_number = self.request.get("phase_number")
    message = cgi.escape(self.request.get("message"))
    site_id = self.request.get("site_id")

    defaults_json = None
    hidden_site_id = None
    if site_id:
      defaults_json = get_personal_information_module_by_site_id(site_id)
      hidden_site_id = '<input type="hidden" id="site_id" name="site_id" value="' + site_id + '">'
      
    if len(message) == 0:
      message = None
    form = None

    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    
    # get site id, get PI data, fill form:
    
    ## on site_db, get_personal_information_by_id
    string = "<h2>No Form Added Yet</h2><p>To add a form for this incident, contact your administrator.</p>"
    label = ""
    paragraph = ""
    phases_links = ""
    submit_button = ""
    if inc_def_query:
      string, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, defaults_json)
  
      phases_links = populate_phase_links(json.loads(inc_def_query.phases_json))

      submit_button = "<button class='submit'>Submit</button>"
    inc_form = None
    if query:
      inc_form = query.form_html
    single_site = single_site_template.render(
        { "form": form,
          "org": org,
          "incident_form_block": string,
          "label": label,
          "paragraph": paragraph,
          "submit_button": submit_button,
          "phases_links": phases_links,
          #"new_form": wt_form()
	})
    self.response.out.write(template.render(
        {"version" : os.environ['CURRENT_VERSION_ID'],
         "message" : message,
         "menubox" : menubox_template.render({"org": org, "event": event, "admin": org.is_admin}),
         "single_site" : single_site,
         "form": form,
         "id": None,
         "page": "/",
         "event_name": event.name,
         "hidden_site_id": hidden_site_id}))

  def AuthenticatedPost(self, org, event):
    post_data = self.request.POST
    site_id = self.request.get("site_id")
    my_string = ""
    for k, v in self.request.POST.iteritems():
      if v == "":
        v = "stub"
      my_string += k + " = '" + v + "', "
      
    phase_id = self.request.get("phase_id")
    
    

    data = site_db.StandardSiteForm(self.request.POST)

    post_dict = dict(self.request.POST)
    post_json = json.dumps(post_dict)
          
    claim_for_org = self.request.get("claim_for_org") == "y"

    data.name.data = site_util.unescape(data.name.data)

    ### SET VALIDATORS HERE
    optional_validator = wtforms.validators.Optional()
    email_validator = wtforms.validators.Email(message=u'Invalid email address.')
    url_validator = wtforms.validators.URL(message=u'Invalid URL.')
    required_validator = wtforms.validators.Length(min = 1, max = 100,  message = "Required Field")
    phone_validator = wtforms.validators.Regexp(r'[^a-zA-Z]+$', flags=0, message=u'Phone number. No letters allowed.')

    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    

    
    forms_json_obj = json.loads(inc_def_query.forms_json)
    phase_number = get_phase_number(forms_json_obj, phase_id)
    wt_form = build_form(json.loads(inc_def_query.forms_json), phase_number)
    wt_data = wt_form(self.request.POST)
    validations_array = []
    for obj in forms_json_obj[phase_number]:
      #raise Exception(forms_json_obj[phase_number])
      if "validations" in obj or "required" in obj:
	_id = str(obj["_id"])
	if "validations" in obj and obj[u"validations"] == 'email':
	  validations_array.append(email_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []
	if "validations" in obj and obj["validations"] == "url":
	  validations_array.append(url_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []
	if "validations" in obj and obj["validations"] == "phone":
	  validations_array.append(phone_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []
	if "required" in obj and obj["required"] == False:
	  validations_array.append(optional_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []  
	if "required" in obj and obj["required"] == True:
	  validations_array.append(required_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []  
    if wt_data.validate():
      # elif site_id
      # elif no site_id
      if str(phase_number) == "0" and inc_def_query.is_version_one_legacy == True:	
	lookup = site_db.Site.gql(
	  "WHERE name = :name and address = :address LIMIT 1",
	  name = data.name.data,
	  address = data.address.data)
	
	site = None
	for l in lookup:
	  # See if this same site is for a different event.
	  # If so, we'll make a new one.
	  if l.event and l.event.name == event.name:
	    site = l
	    break

	if not site:
	  # Save the data, and redirect to the view page
	  site = site_db.Site(address = data.address.data,
			      name = data.name.data)
			      #priority = int(data.priority.data))
	for k, v in self.request.POST.iteritems():
	  #if k not in site_db.STANDARD_SITE_PROPERTIES_LIST:
	    if k == "request_date":
	      date_saved = False
	      try:
		date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
		setattr(site, k, date_object)
		date_saved=True
	      except:
		date_saved=False
		pass
	      if date_saved is False:
		try:
		  v = v.replace("/", "-")
		  date_object = datetime.strptime(v, '%Y-%m-%d')
		  setattr(site, k, date_object)
		  date_saved=True
		except:
		  date_saved=False
		  pass
	      if date_saved is False:
		try:
		  v = v.replace("/", "-")
		  date_object = datetime.strptime(v, '%m-%d-%Y')
		  setattr(site, k, date_object)
		  date_saved=True
		except:
		  date_saved=False
		  pass
	    elif k == "latitude" or k == "longitude":
	      setattr(site, k, float(v))
	    else:
	      setattr(site, k, str(v))
	try:
	  data.populate_obj(site)
	except:
	  pass
	  #raise Exception("populate")
	site.reported_by = org
	if claim_for_org:
	  site.claimed_by = org
	  
	# clear assigned_to if status is unassigned
	if data.status.data == 'Open, unassigned':
	  site.assigned_to = ''
	# attempt to save site

	similar_site = None
	if site.similar(event) and not self.request.get('ignore_similar', None):
	  similar_site = site.similar(event)
	  message = None
	elif site.event or event_db.AddSiteToEvent(site, event.key().id()):
	  setattr(site, "is_legacy_and_first_phase", True)
	  site_db.PutAndCache(site)

	  self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
	  return
	else:
	  message = "Failed to add site to event: " + event.name
      elif site_id != "":
	#look up site by id
	site = site_db.Site.get_by_id(int(site_id))
	if not site:
	  #handle
	  pass
	phase_obj = phase.Phase(incident = inc_def_query.key(), site = site.key(), phase_id = phase_id)
	for k, v in self.request.POST.iteritems():
	  if k not in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	    if k == "work_type":
	      raise Exception(v)
	    #raise Exception(k)
	    setattr(phase_obj, k, str(v))
	try:
	  if phase_obj.status != None:
	    phase_obj.put()
	except:
	  pass
	self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
	
      elif site_id == "":
	site = site_db.Site(address = data.address.data,
			      name = data.name.data)
			      #event = event.key())
	
	for k, v in self.request.POST.iteritems():
	  if k  in site_db.STANDARD_SITE_PROPERTIES_LIST:
	    if k == "request_date":
	      date_saved = False
	      try:
		date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
		setattr(site, k, date_object)
		date_saved=True
	      except:
		date_saved=False
		pass
	      if date_saved is False:
		try:
		  v = v.replace("/", "-")
		  date_object = datetime.strptime(v, '%Y-%m-%d')
		  setattr(site, k, date_object)
		  date_saved=True
		except:
		  date_saved=False
		  pass
	      if date_saved is False:
		try:
		  v = v.replace("/", "-")
		  date_object = datetime.strptime(v, '%m-%d-%Y')
		  setattr(site, k, date_object)
		  date_saved=True
		except:
		  date_saved=False
		  pass
	    elif k == "latitude" or k == "longitude":
	      setattr(site, k, float(v))
	    else:
	      setattr(site, k, str(v))
	
	if event_db.AddSiteToEvent(site, event.key().id()):
	  setattr(site, "is_legacy_and_first_phase", False)
	  site_db.PutAndCache(site)
      	phase_obj = phase.Phase(incident = inc_def_query.key(), site = site.key(), phase_id = phase_id)
	for k, v in self.request.POST.iteritems():
	  if k not in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	    if k == "work_type":
	      raise Exception(v)
	    #raise Exception(k)
	    setattr(phase_obj, k, str(v))
	phase_obj.put()
	self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))

	# get all info.
	# save site stuff to sie
	
	# save phase stuff to phase

	

    else:
      message = "Failed to validate"
      similar_site = None

    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()
    inc_form = None
    if query:
      inc_form = query.form_html

    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    
    phase_id = self.request.get("phase_id")
    forms_array = json.loads(inc_def_query.forms_json)
    phase_number = 0
    i = 0
    for form in forms_array:
      for obj in form:
	if phase_id in str(obj):
	  phase_number = i
	#raise Exception(phase_number)
      i += 1
    submit_button = "<button class='submit'>Submit</button>"
    message = "none"
    string, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, self.request.POST)
    single_site = single_site_template.render(
	{ "form": data,
	  "org": org,
	  "incident_form_block": string,
	  "submit_button": submit_button
	  })
    self.response.out.write(template.render(
	{"message": message,
	"similar_site": None,
	"version" : os.environ['CURRENT_VERSION_ID'],
	"errors": wt_data.errors,
	"menubox" : menubox_template.render({"org": org, "event": event}),
	"single_site": single_site,
	"form": data,
	"id": None,
	"page": "/",
	"post_json": post_json	,
	"event_name": event.name}))

def populate_phase_links(phases_json):
  links = "<h3>Phases</h3>"
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    separator = ""
    if i > 0:
      separator = " | "
    links = links + separator + '<a href="/?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    i+=1
    
  return links

def get_phase_number(form_json, phase_id):
  i = 0
  string = ""
  label = ""
  paragraph = ""
  phase_number = 0
  i = 0
  for obj in form_json:
    for o in obj:
      if "phase_id" in o and o['phase_id'] == phase_id:
	phase_number = i
    i+=1
    
  return phase_number

def build_form(forms_json, phase_number):
  class DynamicForm(wtforms.Form): pass    

  if phase_number:
    phase_number = int(str(phase_number))
  else:
    phase_number = 0
    

  i = 0
  string = ""
  label = ""
  paragraph = ""
  forms_json[phase_number]
  for obj in forms_json[phase_number]:
    if "_id" in obj:
    #if "type" in obj and obj['type'] == 'text':
      #raise Exception(obj)
      setattr(DynamicForm, obj['_id'], TextField(obj['label']))
    #if "type" in obj and obj['type'] == 'textarea':
      #setattr(DynamicForm, obj['_id'], TextAreaField(obj['label']))
    #if "type" in obj and obj['type'] == 'checkbox':
      #setattr(DynamicForm, obj['_id'], BooleanField(obj['label']))
  d = DynamicForm
  return d  

def get_personal_information_module_by_site_id(site_id):
  site = site_db.Site.get_by_id(int(site_id))
  site_dict = site_db.SiteToDict(site)
  personal_info_data = {}
  for field in site_dict:
    if field in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
      personal_info_data[field] = str(site_dict[field])
  return personal_info_data