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
from helpers import phase_helpers
import wtforms.ext.dateutil.fields
import wtforms.fields
from wtforms import Form, BooleanField, TextField, TextAreaField, validators, PasswordField, ValidationError, RadioField, SelectField
from site_db import PERSONAL_INFORMATION_MODULE_ATTRIBUTES

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
menubox_template = jinja_environment.get_template('_menubox.html')
HATTIESBURG_SHORT_NAME = "hattiesburg"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"


class IncidentForm(site_db.Site):
  pass

class FormHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    # Read url parameters
    phase_number = self.request.get("phase_number")
    message = cgi.escape(self.request.get("message"))
    site_id = self.request.get("site_id")

    # if no message, set to none so Jinja knows to ignore it
    if len(message) == 0:
      message = None
      
      
    # variables that are defined if there is a site_id
    # Get personal information already added and prepopulate form
    # add a hidden element to let POST know which site_id to associate with the new phase data
    defaults_json = None
    hidden_site_id = None
    if site_id:
      defaults_json = site_db.get_personal_information_module_by_site_id(site_id)
      hidden_site_id = '<input type="hidden" id="site_id" name="site_id" value="' + site_id + '">'
    
    # get the incident definition for the event associated with this login
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    
    # get the current phase name
    #phase_name = phase_helpers.get_phase_name(json.loads(inc_def_query.forms_json), 0)

    # set up variables that will be passed to the form. The forms label, intro paragraph, links for each phase and the submit button
    string = "<h2>No Form Added Yet</h2><p>To add a form for this incident, contact your administrator.</p>"
    submit_button = "<button class='submit'>Submit</button>"

    label = ""
    paragraph = ""
    phases_links = ""
    if inc_def_query:
      # set above variables from the incident definition's forms_json
      string, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, defaults_json)
  
      phases_links = phase_helpers.populate_phase_links(json.loads(inc_def_query.phases_json), phase_number)
    single_site = single_site_template.render(
        { "org": org,
          "incident_form_block": string,
          "label": label,
          "paragraph": paragraph,
          "submit_button": submit_button,
          "phases_links": phases_links,
	})
    self.response.out.write(template.render(
        {"version" : os.environ['CURRENT_VERSION_ID'],
         "message" : message,
         "menubox" : menubox_template.render({"org": org, "event": event, "admin": org.is_admin}),
         "single_site" : single_site,
         "id": None,
         "page": "/",
         "event_name": event.name,
         "hidden_site_id": hidden_site_id}))


  def AuthenticatedPost(self, org, event):
    # get post data
    post_data = self.request.POST
    phase_id = self.request.get("phase_id")
    claim_for_org = self.request.get("claim_for_org") == "y"
    site_id = self.request.get("site_id")
    similar_site = None    
    message = None




    # get the incident definition forms_json
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()   
    forms_json_obj = json.loads(inc_def_query.forms_json)

    
    # get phase number, and phase name
    phase_number = phase_helpers.get_phase_number(forms_json_obj, phase_id)
    phase_name = phase_helpers.get_phase_name(forms_json_obj, phase_number)


    # retrieve POST data into data variable via the StandardSiteForm
    data = site_db.StandardSiteForm(self.request.POST)
    data.name.data = site_util.unescape(data.name.data)


    # send the post_json variable back in case of invalid form
    post_dict = dict(self.request.POST)
    post_json = json.dumps(post_dict)
          

    ### SET VALIDATORS HERE
    optional_validator = wtforms.validators.Optional()
    email_validator = wtforms.validators.Email(message=u'Invalid email address.')
    url_validator = wtforms.validators.URL(message=u'Invalid URL.')
    required_validator = wtforms.validators.Length(min = 1, max = 100,  message = "Required Field")
    phone_validator = wtforms.validators.Regexp(r'[^a-zA-Z]+$', flags=0, message=u'Phone number. No letters allowed.')

    
    # from incident definition, get forms_json
    wt_form = build_form(forms_json_obj, phase_number)
    wt_data = wt_form(self.request.POST)
    validations_array = []
    
    # set up validations
    for obj in forms_json_obj[phase_number]:
      if "validations" in obj or "required" in obj:
	_id = str(obj["_id"])
	if _id == "work_type":
	  validations_array.append(required_validator)
	  wt_data[_id].validators = wt_data[_id].validators + validations_array
	  validations_array = []  
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
	  
	  
    # test validations
    if wt_data.validate():
      text_areas_list = get_text_areas(json.loads(inc_def_query.forms_json), phase_name)
      
      # if site_id != "" then there is a pre-existing site that we're adding data to
      if site_id != "":
	site = site_db.Site.get_by_id(int(site_id))
	
	# set reported by, and claimed by
	site = site_db.reported_by_for_this_site(site, phase_name, org)
	if claim_for_org:
	  site = site_db.claim_for_this_org(site, phase_name, org)
	  
	# set main site attrs
	for k, v in self.request.POST.iteritems():
	  if k not in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	    if k == "work_type":
	      new_key = "phase_" + phase_name.lower + "_" + k
	      if k in text_areas_list:
	      #raise Exception(1)
		setattr(site, new_key, db.Text(str(v)))
	      else:
		setattr(site, new_key, str(v))
		
	# add this phase to open_phases_list
	old_phases_list = site.open_phases_list
	old_phases_list.append(phase_name.lower())
	setattr(site, "open_phases_list", old_phases_list)
	
	# TODO
	# Check for similar
	if site.similar(event) and not self.request.get('ignore_similar', None):
	  similar_site = site.similar(event)
	  message = "Not saved. Exact match for existing event"
	else:
	  # save and cache the site
	  site_db.PutAndCache(site)
	  
	  # redirect
	  self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
	
      # if there is no site_id, create a new site
      elif site_id == "":
	site = site_db.Site(address = data.address.data,
			      name = data.name.data)
	
	# handle reported_by and claimed_by
	site = site_db.reported_by_for_this_site(site, phase_name, org)
	if claim_for_org:
	  site = site_db.claim_for_this_org(site, phase_name, org)
	
	# set up main site attrs.
	for k, v in self.request.POST.iteritems():
	  if k in site_db.PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	    if k == "work_type":
	      pass
	    elif k == "request_date":
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
	  # set phase specific properties
	  else:
	    new_key = "phase_" + phase_name.lower() + "_" + k
	    # set *_notes properties to TextProperty
	    if k in text_areas_list:
	      setattr(site, new_key, db.Text(str(v)))
	    else:
	      # if not a text property, save as a string
	      setattr(site, new_key, str(v))
	      
	# save this phase to the new site's open_phases_list
	phases_list = []
	phases_list.append(phase_name.lower())
	setattr(site, "open_phases_list", phases_list)
	
	# TODO
	# Check for similar
		
	# add site to event, and cache
	if site.similar(event) and not self.request.get('ignore_similar', None):
	  similar_site = site.similar(event)
	  message = "Not saved. Exact match for existing event"
	elif event_db.AddSiteToEvent(site, event.key().id()):
	  site_db.PutAndCache(site)
	  
	# redirect
	  self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
	else:
	  message = "Failed to add site to event: " + event.name
	  self.redirect("/?message=" + message)
	  

	
    # validation failure
    else:
      message = "Failed to validate"
            
      
    # using the phase_id from the top of the AuthenticatedPost method, get the correct form, populate it via the POST object, and return a new form with the proper errors
    phase_number = 0
    i = 0
    for form in forms_json_obj:
      for obj in form:
	if phase_id in str(obj):
	  phase_number = i
      i += 1
    submit_button = "<button class='submit'>Submit</button>"
    string, label, paragraph= populate_incident_form.populate_incident_form(forms_json_obj, phase_number, self.request.POST)
    single_site = single_site_template.render(
	{ "form": data,
	  "org": org,
	  "incident_form_block": string,
	  "submit_button": submit_button
	  })
    self.response.out.write(template.render(
	{"message": message,
	"similar_site": similar_site,
	"version" : os.environ['CURRENT_VERSION_ID'],
	"errors": wt_data.errors,
	"menubox" : menubox_template.render({"org": org, "event": event}),
	"single_site": single_site,
	"form": data,
	"id": None,
	"page": "/",
	"post_json": post_json	,
	"event_name": event.name}))



def build_form(forms_json, phase_number):
  class DynamicForm(wtforms.Form): pass    

  if phase_number:
    phase_number = int(str(phase_number))
  else:
    phase_number = 0
  forms_json[phase_number]
  for obj in forms_json[phase_number]:
    if "_id" in obj:
      setattr(DynamicForm, obj['_id'], TextField(obj['label']))
  d = DynamicForm
  return d  

def get_text_areas(forms_json, phase_name):
  text_areas_list = []
  # get correct phase
  for obj1 in forms_json:
    for obj in obj1:
      if "type" in obj:
	if obj["type"] == "textarea":
	  text_areas_list.append(str(obj['_id'])) 
  return text_areas_list