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
import wtforms.ext.dateutil.fields
import wtforms.fields
from wtforms import Form, BooleanField, TextField, TextAreaField, validators, PasswordField, ValidationError, RadioField, SelectField




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
    #single_site_template = jinja_environment.get_template('single_site.html')
      
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
      
    #if not event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME, "sandy"]:
      #single_site_template = jinja_environment.get_template('single_site_incident_form.html')

    phase_number = self.request.get("phase_number")
    message = cgi.escape(self.request.get("message"))
    if len(message) == 0:
      message = None
    form = None
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #form = site_db.DerechosSiteForm()
    #else:
      #form = site_db.SiteForm()
      
    # get event.key()
    # search for form with that event
    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    string, label, paragraph= populate_incident_form(json.loads(inc_def_query.forms_json), phase_number)
    phases_links = populate_phase_links(json.loads(inc_def_query.phases_json))
    #wt_form = build_form(json.loads(inc_def_query.forms_json), phase_number)
    #raise Exception(th)
    
    # set it as form_stub
    # send to single site
    #submit_button = '<a id="submit_form" value="Submit request">Submit</a>'
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
         "event_name": event.name}))

  def AuthenticatedPost(self, org, event):
    post_data = self.request.POST
    
    my_string = ""
    for k, v in self.request.POST.iteritems():
      if v == "":
        v = "stub"
      my_string += k + " = '" + v + "', "
    
    
    data = site_db.StandardSiteForm(self.request.POST)
    post_dict = dict(self.request.POST)
    post_json = json.dumps(post_dict)
    
    #single_site_template = jinja_environment.get_template('single_site.html')
      
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
      
    claim_for_org = self.request.get("claim_for_org") == "y"
    #data = None
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
        #data = site_db.DerechosSiteForm(self.request.POST)
    #else:
        #data = site_db.SiteForm(self.request.POST)
        

    # un-escaping data caused by base.py = self.request.POST[i] = cgi.escape(self.request.POST[i])
    data.name.data = site_util.unescape(data.name.data)
    data.priority.data = int(data.priority.data)

    data.name.validators = data.name.validators + [wtforms.validators.Length(min = 1, max = 100,
                             message = "Name must be between 1 and 100 characters")]
    data.phone1.validators = data.phone1.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a primary phone number")]
    data.city.validators = data.city.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a city name")]
    data.state.validators = data.state.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a state name")]
    data.work_type.validators = data.work_type.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please set a primary work type")]
    if data.validate():
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
                            name = data.name.data,
                            priority = int(data.priority.data))
      for k, v in self.request.POST.iteritems():
	if k not in site_db.STANDARD_SITE_PROPERTIES_LIST:
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
	      


	  else:
            setattr(site, k, v)
      try:
	data.populate_obj(site)
      except:
	raise Exception("populate")
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
        site_db.PutAndCache(site)
	#dict_dict_site = site_db.SiteToDict(site)
	#raise Exception(dict_dict_site)
        self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
        return
      else:
        message = "Failed to add site to event: " + event.name
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


    string, label, paragraph= populate_incident_form(IncidentForm, json.loads(inc_def_query.forms_json), phase_number)
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
         "errors": data.errors,
         "menubox" : menubox_template.render({"org": org, "event": event}),
         "single_site": single_site,
         "form": data,
         "id": None,
         "page": "/",
         "post_json": post_json	,
         "event_name": event.name}))



def populate_incident_form(form_json, phase_number):
  i = 0
  string = ""
  label = ""
  paragraph = ""

  if phase_number:
    phase_number = return_phase_number_int(phase_number)

  if not check_if_form_exists(form_json, phase_number):
    string = "<h2>No Form Added</h2>"
    label = ""
    paragraph=""
    return string, label, paragraph

  # If form exists, continue
  
  for obj in form_json[phase_number]:
    i+=1
    
    ### If the object is holding the value of label, set the label.
    if "type" in obj and obj["type"] == "label":
      label = obj['label']
      
    ### If the object is a paragraph, set paragraph variable
    elif "type" in obj and obj["type"] == "paragraph":
      paragraph = obj["paragraph"]
      
    ### If the object is a header, send to get_header_html()
    elif "type" in obj and obj["type"] == "header":
      string = get_header_html(obj, string)
      
    ### If the object is a subheader, send to get_subheader_html()
    elif "type" in obj and obj["type"] == "subheader":
      string = get_subheader_html(obj, string)
      
    ### If the object is holding the phase_id, set the hidden phase_id value
    elif "phase_id" in obj:
      string = get_phase_html(obj, string)
      
    ### If the object is a text field, send to get_text_html() 
    elif "type" in obj and obj["type"] == "text":
      string = get_text_html(obj, string)

    ### If the object is a textarea, send to get_textarea_html()
    elif "type" in obj and obj["type"] == "textarea":
      string = get_textarea_html(obj, string)
    
    ### If the object is a checkbox, send to get_checkbox_html()
    elif "type" in obj and obj["type"] == "checkbox":
      string = get_checkbox_html(obj, string)

    ### if the object is a select, send to get_select_html()
    elif "type" in obj and obj["type"] == "select":
      string = get_select_html(obj, string)
      
    ### if the object is a radio, send to get_radio_html()
    elif "type" in obj and obj["type"] == "radio":
      string = get_radio_html(obj, string)
  
  return string, label, paragraph


def get_text_html(obj, string):
  required = ""
  suggestion = get_suggestion_div(obj["_id"])
  edit_string = force_click_edit(obj["_id"])
  readonly_string = set_readonly(obj["_id"])
  #raise Exception(edit_string)

  if obj["required"] == True:
    required = "*"
  new_text_input = '<tr><td class=question>' +obj['label'] + str(edit_string) + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="text" ' + readonly_string + ' /></div>' + suggestion + '</td></tr>'
  string += new_text_input  
  return string
  
def get_phase_html(obj, string):
  string += '<input type="hidden" name="phase_id" value="%s">' % obj["phase_id"]
  return string

def get_header_html(obj, string):
  new_header = '<tr><td class="question"><h2>%s</h2></tr></td>' % obj['header']
  string += new_header
  return string

def get_subheader_html(obj, string):
  new_subheader = '<tr><td class="question"><h3>%s</h3></tr></td>' % sobj['subheader']
  string += new_subheader
  return string

def get_textarea_html(obj, string):
  new_textarea = '<tr><td class=question>' + obj['label'] + ':</td><td class="answer"><div class="form_field"><textarea class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '"></textarea></div></td></tr>'
  string += new_textarea
  return string

def get_checkbox_html(obj, string):
  required = ""
  checked = ""
  if obj["required"] == True:
    required = "*"
  if obj["_default"] == "y":
    checked = " checked"
  new_checkbox = '<tr><td class=question><label for="' + obj['_id'] + '">' + obj['label'] + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + obj['_id'] + '" type="hidden" value="n"/><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="checkbox" value="y"' + checked + '></div></td></tr>'
  string += new_checkbox
  return string

def get_select_html(obj, string):
  options_array = []
  required = ""
  for key in obj:
    if "select_option_" in key:
      options_array.append(key)
  if obj["required"]:
    required = "*"
  begin_option = '<tr><td class=question>' + obj['label'] + required + '</td><td class="answer"><div class="form_field"><select class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '">'
  end_option = '</select></div></td></tr>'
  select_string = '<option value="None">Choose one</option>'

  options_array.sort()
  for option in options_array:
    option_string = ""
    option_string = "<option>" + obj[option] + "</option>"
    select_string = select_string + option_string

  new_select = begin_option + select_string + end_option
  string += new_select
  return string

def get_radio_html(obj, string):
  options_array = []
  required = ""
  for key in obj:
    if "radio_option_" in key:
      options_array.append(key)
  if obj["required"]:
	  required = "*"
  radio_string = "";
  radio_string_start = '</td></tr><tr><td class=question>' + obj['label'] + required + '</td><td class="answer"><table><tr><td>' + obj["low_hint"] + '</td><td>'
  radio_string_end = '<td>' + obj['high_hint'] + '</td></tr></table></td></tr>'
  options_array.sort()
  for option in options_array:
    options_string = ""
    option_string = '<td><input id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="radio" value="' + obj[option] + '"></td>'
    radio_string = radio_string + option_string
  string = string + radio_string_start + radio_string + radio_string_end
  return string
  
def return_phase_number_int(phase_number):
  if phase_number:
    phase_number = int(str(phase_number))
  else:
    phase_number = 0
  return phase_number
    
def check_if_form_exists(form_json, phase_number):
  try:  
    form_json[phase_number]
    return True
  except:
    return False

def get_suggestion_div(id_string):
  suggestion_string = ""
  if id_string == "city" or id_string == "county" or id_string == "state":
    suggestion_string = '<div id=' + id_string + 'Suggestion></div></td></tr>'
  elif id_string == "zip_code":
    suggestion_string = '<div id=zipCodeSuggestion></div></td></tr>'

  return suggestion_string

def force_click_edit(id_string):
  edit_string = ""
  if id_string == "latitude":
    edit_string = """<small>(<a href="#" onclick="document.getElementById('latitude').readOnly=false; document.getElementById('latitude').focus(); return false;">edit</a>)</small>"""
  elif id_string == "longitude":
    edit_string = """<small>(<a href="#" onclick="document.getElementById('longitude').readOnly=false; document.getElementById('longitude').focus(); return false;">edit</a>)</small>"""
  return edit_string

def set_readonly(id_string):
  readonly_string = ""
  if id_string == "latitude" or id_string == "longitude":
    readonly_string = "readonly"
  return readonly_string
	  
def populate_phase_links(phases_json):
  links = ""
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    links = links + '<a href="/?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    i+=1
    
  return links


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
  
    if "type" in obj and obj['type'] == 'text':
      #raise Exception(obj)
      setattr(DynamicForm, obj['_id'], TextField(obj['label']))
    if "type" in obj and obj['type'] == 'textarea':
      setattr(DynamicForm, obj['_id'], TextAreaField(obj['label']))
    if "type" in obj and obj['type'] == 'checkbox':
      setattr(DynamicForm, obj['_id'], BooleanField(obj['label']))
  d = DynamicForm
  return d  
