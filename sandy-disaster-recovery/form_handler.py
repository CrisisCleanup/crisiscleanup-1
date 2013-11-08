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
import os
import urllib2
import wtforms.validators
from google.appengine.ext import db
import json
from datetime import datetime
from xml.sax.saxutils import unescape

# Local libraries.
import base
import event_db
import site_db
import form_db
import page_db
import site_db

import random

from models import incident_definition
import wtforms.ext.dateutil.fields
import wtforms.fields
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField




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
    new_form = build_form(None)
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
    string, label, paragraph= populate_incident_form(IncidentForm, json.loads(inc_def_query.forms_json), phase_number)
    phases_links = populate_phase_links(json.loads(inc_def_query.phases_json))
    #raise Exception(th)
    
    # set it as form_stub
    # send to single site
    submit_button = '<input type="submit" value="Submit request">'
    inc_form = None
    if query:
      inc_form = query.form_html
    single_site = single_site_template.render(
        { "form": form,
          "org": org,
          "incident_form_block": inc_form,})
    page_blocks = page_db.get_page_block_dict()
    self.response.out.write(
        template.render(dict(
            page_blocks, **{
                "version" : os.environ['CURRENT_VERSION_ID'],
                "message" : message,
                "menubox" : menubox_template.render({"org": org, "event": event, "admin": org.is_admin}),
                "single_site" : single_site,
                "form": form,
                "id": None,
                "page": "/",
                "event_name": event.name
            }
        ))
    )
          #"incident_form_block": string,
          #"label": label,
          #"paragraph": paragraph,
	#})
          "incident_form_block": string,
          "label": label,
          "paragraph": paragraph,
          "submit_button": submit_button,
          "phases_links": phases_links,
          "new_form": new_form
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
    data.name.data = unescape(data.name.data)
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

    string, label, paragraph= populate_incident_form(IncidentForm, json.loads(inc_def_query.forms_json), phase_number)
    single_site = single_site_template.render(
        { "form": data,
          "org": org,
          "incident_form_block": string,
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




def populate_incident_form(IncidentForm, form_json, phase_number):
  #raise Exception(phase_number)
  if phase_number:
    phase_number = int(str(phase_number))
  else:
    phase_number = 0
    

  i = 0
  string = ""
  label = ""
  paragraph = ""
  try:  
    form_json[phase_number]
  except:
    string = "<h2>No Form Added"
    label = ""
    paragraph=""
    return string, label, paragraph
  for obj in form_json[phase_number]:
    #raise Exception(form_json[phase_number])
    i+=1
    if "phase_id" in obj:
      string += '<input type="hidden" name="phase_id" value="' + obj['phase_id'] + '">'
    if "type" in obj and obj["type"] == "text":
      required = ""
      if obj["text_required"] == True:
	required = "*"
      new_text_input = '<tr><td class=question>' + obj['text_label'] + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + obj['text_id'] + '" name="' + obj['text_id'] + '" type="text" value="' + obj['text_default'] + '" placeholder="' + obj['text_placeholder'] + '"/></div></td></tr>'
      string += new_text_input
    elif "type" in obj and obj["type"] == "label":
      label = obj['label']
    elif "type" in obj and obj["type"] == "header":
      new_header = '<tr><td class="question"><h2>' + obj['header'] + '</h2></tr></td>'
      string += new_header
      
    elif "type" in obj and obj["type"] == "subheader":
      new_subheader = '<tr><td class="question"><h3>' + obj['subheader'] + '</h3></tr></td>'
      string += new_subheader
    elif "type" in obj and obj["type"] == "textarea":
      new_textarea = '<tr><td class=question>' + obj['textarea_label'] + ':</td><td class="answer">\
      <div class="form_field"><textarea class="" id="' + obj['textarea_id'] + '" name="' + obj['textarea_id'] + '"></textarea></div>\
      </td></tr>'
      string += new_textarea
    
    elif "type" in obj and obj["type"] == "paragraph":
      paragraph = obj["paragraph"]
    elif "type" in obj and obj["type"] == "checkbox":
      required = ""
      checked = ""
      if obj["checkbox_required"] == True:
	required = "*"
      if obj["checkbox_default"] == "y":
	checked = " checked"
      new_checkbox = '<tr><td class=question><label for="' + obj['checkbox_id'] + '">' + obj['checkbox_label'] + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + obj['checkbox_id'] + '" type="hidden" value="' +obj['checkbox_unchecked_value'] + '"/><input class="" id="' + obj['checkbox_id'] + '" name="' + obj['checkbox_id'] + '" type="checkbox" value="' +obj['checkbox_checked_value'] + '"' + checked + '></div></td></tr>';
      string += new_checkbox
    elif "type" in obj and obj["type"] == "select":
      options_array = []
      required = ""
      for key in obj:
	if "select_option_" in key:
	  options_array.append(key)
      if obj["select_required"]:
	required = "*"
      begin_option = '<tr><td class=question>' + obj['select_label'] + required +'</td><td class="answer"><div class="form_field"><select class="" id="' + obj['select_id'] + '" name="' + obj['select_id'] + '">';
      end_option = '</select></div></td></tr>';
      select_string = "";
      
      options_array.sort()
      for option in options_array:
	option_string = ""
	if obj['select_default'] == option:
	  option_string = "<option selected>" + obj[option] + "</option>"
	else:
	  option_string = "<option>" + obj[option] + "</option>";
	select_string = select_string + option_string

      new_select = begin_option + select_string + end_option
      string += new_select
    elif "type" in obj and obj["type"] == "radio":
      options_array = []
      required = ""
      for key in obj:
	if "radio_option_" in key:
	  options_array.append(key)
      if obj["radio_required"]:
	      required = "*"
      radio_string = "";
      radio_string_start = '</td></tr><tr><td class=question>' + obj['radio_label'] + required + '</td><td class="answer"><table><tr><td>' + obj['radio_low_hint'] + '</td><td>';
      radio_string_end = '<td>' + obj['radio_high_hint'] + '</td></tr></table></td></tr>';
      
      options_array.sort()
      for option in options_array:
	options_string = ""
	if obj['radio_default'] == option:
	  option_string = '<td><input id="' + obj['radio_id'] + '" name="' + obj['radio_id'] + '" type="radio" value="' + obj[option] + '" checked="true"></td>'
	else:
	  option_string = '<td><input id="' + obj['radio_id'] + '" name="' + obj['radio_id'] + '" type="radio" value="' + obj[option] + '"></td>';
  
        radio_string = radio_string + option_string
        
      string = string + radio_string_start + radio_string + radio_string_end;
  
      #for (var j = 0; j < options_array.length; j++) {
        #var options_string = "";
	#if(form_json_array[i].radio_default == options_array[j]) {
          #var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '" checked="true"></td>';
	#} else {
	  #var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '"></td>';
	#}

	#radio_string = radio_string + option_string;
      #}

    #if(form_json_array[i].type == "radio") {
      #var options_array = []
      #for (var key in form_json_array[i]) {
        #var key_string = key.toString();
        #if (key_string.indexOf("radio_option_") == 0) {
	    #options_array.push(key_string);
        #}
      #}
      
      #var req = "";
      #if (form_json_array[i].radio_required) {
        #req = "*";
      #}
      #var radio_string = "";
      #var radio_string_start = '</td></tr><tr><td class=question>' + form_json_array[i].radio_label + req + '</td><td class="answer"><table><tr><td>' + form_json_array[i].radio_low_hint + '</td><td>';
      #var radio_string_end = '<td>' + form_json_array[i].radio_high_hint + '</td></tr></table></td></tr>';
      #for (var j = 0; j < options_array.length; j++) {
        #var options_string = "";
	#if(form_json_array[i].radio_default == options_array[j]) {
          #var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '" checked="true"></td>';
	#} else {
	  #var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '"></td>';
	#}

	#radio_string = radio_string + option_string;
      #}
      #var final_radio_string = radio_string_start + radio_string + radio_string_end;
      #$("#form_table").append(final_radio_string);

    #}

  return string, label, paragraph

	
      #if str(obj['type']) == "text":
	#setattr(F,"name", TextField("Name"))
      #except:
	#pass
      #if i == 5:
	#if obj['type'] == "text":
	  #raise Exception("#$#")
	#raise Exception(obj['type'])
      #try:
	#if i == 5:
	  #raise Exception(34)

	  
def populate_phase_links(phases_json):
  links = ""
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    links = links + '<a href="/?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    i+=1
    
  return links



def build_form(form_json):
  
  #for field in form_json:
    ## setattr

  class DynamicForm(Form): pass
  name = "name"
  setattr(DynamicForm, name, TextField(name.title(), [wtforms.validators.Length(min = 1, max = 100,
  message = "New Thing must be between 1 and 100 characters")]))
  
  
  return DynamicForm
