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
from models import phase as phase_model
from helpers import populate_incident_form
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
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    if inc_def_query:
      #raise Exception(id)
      phases_links = populate_phase_links(json.loads(inc_def_query.phases_json), id)

    
    if not phase:
      single_site = single_site_template.render(
	{ "org": org,
	  "phases_links": "<u>Choose a phase from below to edit<u><br>" + phases_links,
	  "message": "Choose a phase from below to edit"
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
    if not id and case_number:
	q = db.GqlQuery("SELECT * FROM Site WHERE case_number=:1", case_number)
	if q.count() == 1:
	    id = q[0].key().id()

    # if no id, 404
    if id is None:
      self.response.set_status(404)
      return

    # load site
    site = site_db.GetAndCache(int(id))
    if not site:
      self.response.set_status(404)
      return
      
    if not site.event.key() == event.key():
	self.redirect("/sites?message=The site you are trying to edit doesn't belong to the event you are signed in to. If you think you are seeing this message in error, contact your administrator")
	return
    #form = site_db.SiteForm(self.request.POST, site)
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #form = site_db.DerechosSiteForm(self.request.POST, site)
    post_json2 = site_db.SiteToDict(site)

    date_string = str(post_json2['request_date'])
    post_json2['request_date'] = date_string
    post_json2['event'] = site.event.name
    
    remove_array = []
    for attr in post_json2:
      if attr not in PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
	remove_array.append(attr)
	
    for attr in remove_array:
      del post_json2[attr]


    phase_id = get_phase_id(json.loads(inc_def_query.forms_json), phase)
    q = db.Query(phase_model.Phase)
    q.filter("phase_id =", phase_id)
    phase_query = q.get()
    PHASE_ATTR_LIST = "incident", "phase_id", "site"
    if phase_query:
      ## Add info to post_json
      phase_dict = phase_model.PhaseToDict(phase_query)
      for attr in phase_dict:
	if attr not in PHASE_ATTR_LIST:
	  post_json2[attr] = phase_dict[attr]
    ################
    # TODO
    #
    # get phase info here, and add to post_json2
    #
    ################
    post_json = json.dumps(post_json2)


    inc_form = None
    form=None
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    if inc_def_query:
      #raise Exception(id)
      phases_links = populate_phase_links(json.loads(inc_def_query.phases_json), id)

    phase_id = None
    try:
      phase_id = post_json2['phase_id']
    except:
      pass
    

    phase_number = phase_number_get
    hidden_elements = {
      "site_id": id,
      "phase_number": phase_number
    }
    
    
    inc_form, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, post_json, hidden_elements = hidden_elements)
    
    #raise Exception(inc_form)
    #raise Exception(post_json)
    submit_button = '<input type="submit" value="Submit request">'
    
    if mode_js:
      submit_button = ""
    #raise Exception(phase)
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
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
    mode_js = False
    phase_id = self.request.get("phase_id")
    
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

    phase_number = get_phase_number(json.loads(inc_def_query.forms_json), phase_id)
    
    
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
      q = db.Query(phase_model.Phase)
      q.filter("site =", site.key())
      q.filter("phase_id =", phase_id)
      phase_entity = q.get()

      # RETURNING WRONG SITE.
      for k, v in self.request.POST.iteritems():
	if k in site_db.PERSONAL_INFORMATION_MODULE_ATTRIBUTES:
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
	  setattr(phase_entity, k, str(v))


      #pass
      
    ### TODO
    #
    # Get data
    # find out if legacy
    # if not legacy, separate into PI and PhI
    # save to PI to correct site and PhI to correct phase
    #
    ###
    #raise Exception(data.data)
    
    #setattr(site, "longitude", lng_float)
    #setattr(site, "latitude", lat_float)
    # Save the data, and redirect to the view page
    for f in data:
      # In order to avoid overriding fields that didn't appear
      # in this form, we have to only set those that were explicitly
      # set in the post request.
      in_post = self.request.get(f.name, default_value = None)
      if in_post is None:
	continue
      
      
      
      if f.name == "request_date":
	date_saved = False
	try:
	  date_object = datetime.strptime(f.data, '%Y-%m-%d %H:%M:%S')
	  setattr(site, f.name, date_object)
	  date_saved=True
	except:
	  date_saved=False
	  pass
	if date_saved is False:
	  try:
	    f.data = f.data.replace("/", "-")
	    date_object = datetime.strptime(f.data, '%Y-%m-%d')
	    setattr(site, f.name, date_object)
	    date_saved=True
	  except:
	    date_saved=False
	    pass
	if date_saved is False:
	  try:
	    f.data = f.data.replace("/", "-")
	    date_object = datetime.strptime(f.data, '%m-%d-%Y')
	    setattr(site, f.name, date_object)
	    date_saved=True
	  except:
	    date_saved=False
	    pass
      elif f.name == "latitude" or f.name == "longitude":
	setattr(site, f.name, float(f.data))
      else:
	setattr(site, f.name, f.data)
    #if claim_for_org:
        #site.claimed_by = org
      # clear assigned_to if status is unassigned
      #if data.status.data == 'Open, unassigned':
        #site.assigned_to = ''
        
        
      for k, v in self.request.POST.iteritems():
	if k not in site_db.STANDARD_SITE_PROPERTIES_LIST:

	  if k == "request_date":
	    try:
	      date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
	      setattr(site, k, date_object)
	    except:
	      date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
	      setattr(site, k, date_object)
	  else:
            setattr(site, k, v)
      site_db.PutAndCache(site)
      if mode_js:
        # returning a 200 is sufficient here.
        return
      else:
        self.redirect('/map?id=%d' % id)
    else:
      q = db.Query(form_db.IncidentForm)
      q.filter("incident =", event.key())
      query = q.get()

      # set it as form_stub
      # send to single site

      inc_form = None
      form=None
      if query:
	inc_form = query.form_html
	
      post_json2 = site_db.SiteToDict(site)
      date_string = str(post_json2['request_date'])
      post_json2['request_date'] = date_string
      post_json2['event'] = site.event.name
      #post_json = {
	#"city": str(site.city),
	#"name": str(site.name),
	#"reported_by": str(site.reported_by.name),
      #}
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

def get_phase_id(form_json, phase_number):
  phase_number = int(phase_number)
  i = 0
  phase_id = ""
  for obj in form_json:
    if phase_number == i:
      for data in obj:
	if 'phase_id' in data:
	  phase_id = data["phase_id"]
    i += 1
  return phase_id
    

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

def populate_phase_links(phases_json, site_id):
  links = "<h3>Phases</h3>"
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    separator = ""
    if i > 0:
      separator = " | "
    links = links + separator + '<a href="/edit?id=' + site_id + '&phase=' + str(i) + '">' + phase['phase_name'] + '</a>'
    i+=1
    
  return links