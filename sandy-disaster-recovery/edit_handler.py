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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
menubox_template = jinja_environment.get_template('_menubox.html')
HATTIESBURG_SHORT_NAME = "derechos"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"

class EditHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    #single_site_template = jinja_environment.get_template('single_site.html')
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')

    # lookup by id or case_number
    id = self.request.get('id', None)
    mode_js = self.request.get("mode") == "js"
    case_number = self.request.get('case', None)
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
    #post_json = {
      #"city": str(site.city),
      #"name": str(site.name),
      #"reported_by": str(site.reported_by.name),
    #}
    post_json = json.dumps(post_json2)
    #raise Exception(post_json)
    


    # set it as form_stub
    # send to single site

    inc_form = None
    form=None
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    phase_id = None
    try:
      phase_id = post_json2['phase_id']
    except:
      pass

    inc_form, label, paragraph= populate_incident_form(json.loads(inc_def_query.forms_json), phase_id)

    submit_button = '<input type="submit" value="Submit request">'


    
    single_site = single_site_template.render(
        { "form": form,
          "org": org,
	  "incident_form_block": inc_form,
	  "post_json": post_json,
	  "submit_button": submit_button
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
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get_by_id(id)
    data = site_db.StandardSiteForm(self.request.POST, site)
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
        #form = site_db.DerechosSiteForm(self.request.POST, site)

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


    case_number = site.case_number
    claim_for_org = self.request.get("claim_for_org") == "y"

    mode_js = self.request.get("mode") == "js"
    if data.validate():
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
        setattr(site, f.name, f.data)
      if claim_for_org:
        site.claimed_by = org
      # clear assigned_to if status is unassigned
      if data.status.data == 'Open, unassigned':
        site.assigned_to = ''
        
        
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
      

      single_site = single_site_template.render(
          { "form": data,
            "org": org,
	    "incident_form_block": inc_form,
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


def populate_incident_form(form_json, phase_id):

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
  for obj in form_json[phase_number]:
    #raise Exception(form_json[phase_number])
    i+=1
    if "phase_id" in obj:
      string += '<input type="hidden" name="phase_id" value="' + obj['phase_id'] + '">'
    if "type" in obj and obj["type"] == "text":
      required = ""
      if obj["required"] == True:
	required = "*"
      new_text_input = '<tr><td class=question>' + obj['label'] + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="text" /></div></td></tr>'
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
      new_textarea = '<tr><td class=question>' + obj['label'] + ':</td><td class="answer">\
      <div class="form_field"><textarea class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '"></textarea></div>\
      </td></tr>'
      string += new_textarea
    
    elif "type" in obj and obj["type"] == "paragraph":
      paragraph = obj["paragraph"]
    elif "type" in obj and obj["type"] == "checkbox":
      required = ""
      checked = ""
      if obj["required"] == True:
	required = "*"
      if obj["_default"] == "y":
	checked = " checked"
      new_checkbox = '<tr><td class=question><label for="' + obj['_id'] + '">' + obj['label'] + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + obj['_id'] + '" type="hidden" value="n"/><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="checkbox" value="y"' + checked + '></div></td></tr>';
      string += new_checkbox
    elif "type" in obj and obj["type"] == "select":
      options_array = []
      required = ""
      for key in obj:
	if "select_option_" in key:
	  options_array.append(key)
      if obj["required"]:
	required = "*"
      begin_option = '<tr><td class=question>' + obj['label'] + required +'</td><td class="answer"><div class="form_field"><select class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '">';
      end_option = '</select></div></td></tr>';
      select_string = '<option value="None">Choose one</option>';
      
      options_array.sort()
      for option in options_array:
	option_string = ""
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
      if obj["required"]:
	      required = "*"
      radio_string = "";
      radio_string_start = '</td></tr><tr><td class=question>' + obj['label'] + required + '</td><td class="answer"><table><tr><td>' + obj['low_hint'] + '</td><td>';
      radio_string_end = '<td>' + obj['high_hint'] + '</td></tr></table></td></tr>';
      
      options_array.sort()
      for option in options_array:
	options_string = ""
	#if obj['radio_default'] == option:
	  #option_string = '<td><input id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="radio" value="' + obj[option] + '" checked="true"></td>'
	#else:
	option_string = '<td><input id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="radio" value="' + obj[option] + '"></td>';
  
        radio_string = radio_string + option_string
        
      string = string + radio_string_start + radio_string + radio_string_end;
  
  return string, label, paragraph
