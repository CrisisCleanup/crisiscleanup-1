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
    
    
    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()

    # set it as form_stub
    # send to single site

    inc_form = None
    form=None
    
    
    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()
    
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    phase_id = None
    try:
      phase_id = post_json2['phase_id']
    except:
      pass

    inc_form, label, paragraph= populate_incident_form(json.loads(inc_def_query.forms_json), phase_id)
    if query:
      inc_form = query.form_html
    new_inc_form = inc_form.replace("checked ", "")
    if 1==1:
      new_inc_form = new_inc_form.replace('<input type="checkbox" id="ignore_similar" name="ignore_similar">', "")
      new_inc_form = new_inc_form.replace('Ignore similar matches', '')
      new_inc_form = new_inc_form.replace('<input type=submit value="Submit request">', '')
  
      #raise Exception(post_json2)

      for k, v in post_json2.iteritems():
	if k in ["request_date", "name", "city", 'county', 'country', 'state', 'address', 'zip_code', 'latitude', 'longitude', 'cross_street', 'phone1', 'phone2', 'time_to_call', 'tarps_needed', 'damaged_fence_length', 'fence_type', 'fence_notes', 'assigned_to', 'total_volunteers', 'hours_worked_per_volunteer', 'initials_of_resident_present', 'prepared_by', 'do_not_work_before', 'flood_height']:
	  try:
	    id_index = new_inc_form.index('id="' + k)
	    value_index = new_inc_form[id_index:].index("value")
	    if k in ["latitude", "longitude"] and event.short_name != "moore":
	      new_inc_form = new_inc_form[:id_index + value_index+7] + str(v) + new_inc_form[id_index + value_index+10:] 
	    else:
	      new_inc_form = new_inc_form[:id_index + value_index+7] + str(v) + new_inc_form[id_index + value_index+7:] 
	  except:
	    pass
	elif k=="special_needs" or k == "notes" or k == "other_hazards" or k =="status_notes" or k== 'goods_and_services' or k=="work_requested":
	  try:
	    id_index = new_inc_form.index('id="' + k)
	    value_index = new_inc_form[id_index:].index(">")
	    new_inc_form = new_inc_form[:id_index + value_index+1] + str(v) + new_inc_form[id_index + value_index+1:] 
	  except:
	    pass

	elif k in ['house_affected', 'outbuilding_affected', 'exterior_property_affected', 'work_without_resident', 'member_of_assessing_organization', 'first_responder', 'older_than_60', 'house_roof_damage', 'outbuilding_roof_damage', 'help_install_tarp', 'interior_debris_removal', 'nonvegitative_debris_removal', 'vegitative_debris_removal', 'unsalvageable_structure', 'heavy_machinery_required', 'habitable', 'electricity', 'electrical_lines', 'unsafe_roof', 'unrestrained_animals', 'claim_for_org', 'disabled', 'hardwood_floor_removal', 'drywall_removal', 'heavy_item_removal', 'appliance_removal', 'standing_water', 'mold_remediation', 'pump_needed', 'roof_damage', "debris_removal_only", "broken_glass", "carpet_removal"]:
	  try:
	    if v == "y":
	      id_index = new_inc_form.index('id="' + k)
	      value_index = new_inc_form[id_index:].index(">")
	      new_inc_form = new_inc_form[:id_index + value_index] + "checked" + new_inc_form[id_index + value_index:] 
	  except:
	    pass
	    
	    
	#TODO
	#
	# Below deleted pending correct form. Make a real form
	#
	
	
	#elif k=="priority" or k=="destruction_level":
	  ##try:
	  #id_index = new_inc_form.index('name="' + k + '" type="radio" value="' + str(v))
	  ##new_inc_form = new_inc_form[id_index-350:id_index+350].replace("checked ", "")

	  #new_inc_form = new_inc_form[:id_index] + " checked " + new_inc_form[id_index:] 
	#elif k in ["work_type", "rent_or_own", "num_trees_down", "num_wide_trees", "status", 'floors_affected']:
	  #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME] and k == "floors_affected":
	    #pass
	  #else:
	    #logging.debug(event.short_name)
	    #logging.debug(k + " is the key")
            #logging.debug(v + " is the value")
	    #id_index = new_inc_form.index('id="' + k)
	    #value_index = new_inc_form[id_index:].index('value="' + str(v))
	    #length = 0
	    #if v != None:
	      #length = len(str(v))
	    
	    #new_inc_form = new_inc_form[:id_index + value_index+8 + length] + "selected" + new_inc_form[id_index + value_index+8 + length:] 

	  


	
	#raise Exception(new_inc_form[:id_index + 380])
	#except:
	  #pass      # find 'id=" + k
      # find type=", (index)
      # find ", (index)
      # What's in between is the type.
      # If the type == Checkbox, and value == y
      # find >, (index)
      # add "checked" just before
    submit_button = '<input type="submit" value="Submit request">'

    single_site = single_site_template.render(
        { "form": form,
          "org": org,
	  "incident_form_block": new_inc_form,
	  "post_json": post_json,
	  "submit_button": submit_button
          })
    
    #raise Exception(query.form_html)
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
    i+=1
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
	  option_string = '<td><input id="' + obj[option] + '" name="' + obj['radio_label'] + '" type="radio" value="' + obj[option] + '" checked="true"></td>'
	else:
	  option_string = '<td><input id="' + obj['radio_label'] + '" name="' + obj['radio_label'] + '" type="radio" value="' + obj['radio_label'] + '"></td>';
  
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
