##!/usr/bin/env python
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
import jinja2
import logging
import os
from google.appengine.ext import db
import json
import wtforms.validators
from datetime import datetime


# Local libraries.
import base
import site_db
import site_util
import form_db
from models import incident_definition
from helpers import populate_incident_form
from helpers import phase_helpers
from wtforms import Form, BooleanField, TextField, TextAreaField, validators, PasswordField, ValidationError, RadioField, SelectField


PERSONAL_INFORMATION_MODULE_ATTRIBUTES = ["name", "request_date", "address", "city", "state", "county", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_organization", "first_responder", "older_than_60", "disabled", "special_needs", "priority"]

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
menubox_template = jinja_environment.get_template('_menubox.html')
HATTIESBURG_SHORT_NAME = "derechos"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"

class EditHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    
    id = self.request.get('id', None)
    mode_js = self.request.get("mode") == "js"
    case_number = self.request.get('case', None)
    phase = self.request.get("phase")
    phase_number_get = self.request.get("phase")
    
    # Use the incident definition get a set of links for each phase, to be passed to the form
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    if inc_def_query:
      phases_links = phase_helpers.populate_phase_links_edit_html(json.loads(inc_def_query.phases_json), id)

    
    # if not phase, that means we will just show the edit template, and allow the user to select whih phase they want to edit
    if not phase:
      single_site = single_site_template.render(
	{ "org": org,
	  "phases_links": "<u>Choose a phase from below to edit<u><br>" + phases_links,
	})
	
		  
      self.response.out.write(template.render(
	    {"mode_js": self.request.get("mode") == "js",
	    "menubox" : menubox_template.render({"org": org, "event": event}),
	    "single_site": single_site,
	    "event_name": event.name,
	    #"form": form,
	    "id": id,
	    #"post_json": post_json	,
	    "page": "/edit"}))
      return
    
    # if we have a case_number but not the site id, use the case_number to retrieve it
    if not id and case_number:
	q = db.GqlQuery("SELECT * FROM Site WHERE case_number=:1", case_number)
	if q.count() == 1:
	    id = q[0].key().id()

    # if still no id, 404
    if id is None:
      self.response.set_status(404)
      return

    # load site
    site = site_db.GetAndCache(int(id))
    if not site:
      self.response.set_status(404)
      return
      
    # don't return the site if the user isn't signed in to the corresponding event
    if not site.event.key() == event.key():
	self.redirect("/sites?message=The site you are trying to edit doesn't belong to the event you are signed in to. If you think you are seeing this message in error, contact your administrator")
	return
      
    # get the site info into a python object, get the phase name and set the phase prefix
    site_dict = site_db.SiteToDict(site)
    post_json_final = {}
    phase_name = phase_helpers.get_phase_name(json.loads(inc_def_query.forms_json), phase_number_get).lower()
    phase_prefix = "phase_" + phase_name + "_"
    for obj in site_dict:
      if phase_prefix in obj:
	new_attr = obj.replace(phase_prefix, "")
	post_json_final[new_attr] = site_dict[obj]
      else:
	post_json_final[obj] = site_dict[obj]
    site_dict = post_json_final

    # add the date and te event name
    date_string = str(site_dict['request_date'])
    site_dict['request_date'] = date_string
    site_dict['event'] = site.event.name

    # convert to json
    post_json = json.dumps(site_dict)

    # initialize the form variables
    inc_form = None
    form=None
    
    # get phases_links
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    if inc_def_query:
      phases_links = phase_helpers.populate_phase_links_edit_html(json.loads(inc_def_query.phases_json), id)

    # get the phase_id
    phase_id = None
    try:
      phase_id = site_dict['phase_id']
    except:
      pass
    
    
    # get the phase_number and load the hidden elements that will be passed to the form
    phase_number = phase_number_get
    hidden_elements = {
      "site_id": id,
      "phase_number": phase_number
    }
    
    
    # get the form, label and paragraph to send to the form
    inc_form, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, post_json, hidden_elements = hidden_elements)
    

    submit_button = '<input type="submit" value="Submit request">'
    
    if mode_js:
      submit_button = ""
      
      
      
    if phase:
      single_site = single_site_template.render(
	  { "form": form,
	    "org": org,
	    "incident_form_block": inc_form,
	    "post_json": post_json,
	    "submit_button": submit_button, 
	    "phases_links": phases_links
	  })
    else: 
	single_site = single_site_template.render(
	  { "org": org,
	    "phases_links": phases_links
	  })
      
    self.response.out.write(template.render(
	  {"mode_js": self.request.get("mode") == "js",
	  "menubox" : menubox_template.render({"org": org, "event": event}),
	  "single_site": single_site,
	  "event_name": event.name,
	  "form": form,
	  "id": id,
	  "post_json": post_json	,
	  "page": "/edit"}))



  def AuthenticatedPost(self, org, event):
    phase_id = self.request.get("phase_id")

    # get the incident definition forms_json
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()   
    forms_json_obj = json.loads(inc_def_query.forms_json)

    
    # get phase number, and phase name
    phase_number = phase_helpers.get_phase_number(forms_json_obj, phase_id)
    phase_name = phase_helpers.get_phase_name(forms_json_obj, phase_number)
    
    
    mode_js = False
    
    site_id = self.request.get("site_id")
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    #raise Exception(inc_def_query.forms_json)
    ### SET VALIDATORS HERE
    optional_validator = wtforms.validators.Optional()
    email_validator = wtforms.validators.Email(message=u'Invalid email aress.')
    url_validator = wtforms.validators.URL(message=u'Invalid URL.')
    required_validator = wtforms.validators.Length(min = 1, max = 100,  message = "Required Field")
    phone_validator = wtforms.validators.Regexp(r'^\d+$', flags=0, message=u'Phone number. No letters allowed or other characters allowed.')

    phase_number = phase_helpers.get_phase_number(json.loads(inc_def_query.forms_json), phase_id)
    
    
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get_by_id(id)
    #raise Exception(id)
    wt_form = build_form(json.loads(inc_def_query.forms_json), phase_number)
    data = wt_form(self.request.POST, site)
    validations_array = []
    forms_json_obj = json.loads(inc_def_query.forms_json)

    for obj in forms_json_obj[phase_number]:
      #raise Exception(forms_json_obj[phase_number])
      if "validations" in obj or "required" in obj:
	_id = str(obj["_id"])
	if "validations" in obj and obj[u"validations"] == 'email':
	  validations_array.append(email_validator)
	  data[_id].validators = data[_id].validators + validations_array
	  validations_array = []
	if "validations" in obj and obj["validations"] == "url":
	  validations_array.append(url_validator)
	  data[_id].validators = data[_id].validators + validations_array
	  validations_array = []
	if "validations" in obj and obj["validations"] == "phone":
	  validations_array.append(phone_validator)
	  data[_id].validators = data[_id].validators + validations_array
	  validations_array = []
	if "required" in obj and obj["required"] == False:
	  validations_array.append(optional_validator)
	  data[_id].validators = data[_id].validators + validations_array
	  validations_array = []  
	if "required" in obj and obj["required"] == True:
	  validations_array.append(required_validator)
	  data[_id].validators = data[_id].validators + validations_array
	  validations_array = []  


    if data.validate():
      text_areas_list = get_text_areas(json.loads(inc_def_query.forms_json), phase_name)

      for k, v in self.request.POST.iteritems():
	if k in site_db.PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	  #raise Exception(1)
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
	else:
	  new_key = "phase_" + phase_name.lower() + "_" + k
	    # set *_notes properties to TextProperty
	  if k in text_areas_list:
	    setattr(site, new_key, db.Text(str(v)))
	  else:
	    # if not a text property, save as a string
	    setattr(site, new_key, str(v))
	  claim_for = new_key + "_claim_for_org"
	  claimed_by = new_key + "_claimed_by"
	  if claim_for == "n":
	    claimed_by = None
	    
	      
	    
      site_db.PutAndCache(site)
      if mode_js:
        return
      else:
        self.redirect('/map?id=%d' % id)
    else:
      q = db.Query(form_db.IncidentForm)
      q.filter("incident =", event.key())
      query = q.get()

      inc_form = None
      form=None
      if query:
	inc_form = query.form_html
	
      post_json2 = site_db.SiteToDict(site)
      date_string = str(post_json2['request_date'])
      post_json2['request_date'] = date_string
      post_json2['event'] = site.event.name
      post_json = json.dumps(post_json2)
      
      submit_button = "<button class='submit'>Submit</button>"

      single_site = single_site_template.render(
          { "new_form": data,
            "org": org,
	    "incident_form_block": inc_form,
	    "submit_button": submit_button
	  })
      if mode_js:
        self.response.set_status(400)
      
      self.response.out.write(template.render(
          {"mode_js": mode_js,
           "menubox" : menubox_template.render({"org": org, "event": event}),
           "errors": data.errors,
           "form": data,
           "single_site": single_site,
           "id": id,
	   "post_json": post_json,
           "page": "/edit"}))


    

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

def get_text_areas(forms_json, phase_name):
  text_areas_list = []
  # get correct phase
  for obj1 in forms_json:
    for obj in obj1:
      if "type" in obj:
	if obj["type"] == "textarea":
	  text_areas_list.append(str(obj['_id'])) 
  return text_areas_list