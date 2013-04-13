#!/usr/bin/env python
#
# Copyright 2012 Andy Gimma
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
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField

import cgi
import jinja2
import logging
import os
import urllib2
import wtforms.validators
import HTMLParser


# Local libraries.
import base
import event_db
import site_db
import site_util
import cache
import form_db
import event_db

from datetime import datetime
import settings

from google.appengine.ext import db
import organization
import primary_contact_db
import random_password
import incident_csv_db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_create_incident_form.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
cache_time = 60 * 60
HTML_PARSER = HTMLParser.HTMLParser()
PROPERTIES_LIST = []

class AdminCreateIncidentFormHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return
            
	query_string = "SELECT * FROM Event"
	events = db.GqlQuery(query_string)
        self.response.out.write(template.render(
        {
	  "event_results": events,
        }))
        return
        
        
    def AuthenticatedPost(self, org, event):
	global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return
      
	incident_id = self.request.get("choose_incident")
	incident_form_html = self.request.get("incident_form_html")
	if incident_form_html:
	  incident_form_html = HTML_PARSER.unescape(incident_form_html)

	
	
	incident = event_db.Event.get_by_id(int(incident_id))
	primary_form_html = """
	<div id="similars"></div>
	<h2>Personal Information</h2>
	<table>
	<tr><td class=question>Resident name: <span class=required-asterisk>*</span></td>
	<td class="answer">
	  <div class="form_field">
	    <input class="" id="name" name="name" type="text" value="">
	  </div>
	</td></tr>
	<tr><td class=question>Date of Request:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="request_date" name="request_date" type="text" value="2013-04-01 17:15">
	  </div>
	</td></tr>
	<tr><td class=question>Street Address:<span class=required-asterisk>*</span></td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="address" name="address" type="text" value="">
	  </div>
	</div></td></tr>
	<tr><td class=question>City:<span class=required-asterisk>*</span></td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="city" name="city" type="text" value="">
	  </div>
	<div id=citySuggestion></div></td></tr>
	<tr><td class=question>County:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="county" name="county" type="text" value="">
	  </div>
	<div id=countySuggestion></div></td></tr>
	<tr><td class=question>State:<span class=required-asterisk>*</span></td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="state" name="state" type="text" value="">
	  </div>
	<div id=stateSuggestion></div></td></tr>
	<tr><td class=question>Zip Code:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="zip_code" name="zip_code" type="text" value="">
	  </div>
	<div id=zipCodeSuggestion></td></tr>
	<tr>
	  <td class=question>
	    Latitude:
	    <small>(<a href="#" onclick="document.getElementById('latitude').readOnly=false; document.getElementById('latitude').focus(); return false;">edit</a>)</small>
	  </td>
	  <td class="answer">
	  <div class="form_field">
	    <input class="" id="latitude" name="latitude" readonly type="text" value="0.0">
	  </div>
	</td>
	</tr>
	<tr>
	  <td class=question>
	    Longitude:
	    <small>(<a href="#" onclick="document.getElementById('longitude').readOnly=false; document.getElementById('longitude').focus(); return false">edit</a>)</small>
	  </td>
	  <td class="answer">
	  <div class="form_field">
	    <input class="" id="longitude" name="longitude" readonly type="text" value="0.0">
	  </div>
	</td>
	</tr>
	<tr><td class=question>Cross Street or Nearby Landmark:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="cross_street" name="cross_street" type="text" value="">
	  </div>
	</td></tr>
	<tr><td class=question>Phone Numbers:<span class=required-asterisk>*</span></td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="phone1" name="phone1" type="text" value="">
	  </div>
	  <div class="form_field">
	    <input class="" id="phone2" name="phone2" type="text" value="">
	  </div>
	</td></tr>
	<tr><td class=question>Best time to call:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="time_to_call" name="time_to_call" type="text" value="">
	  </div>
	</td></tr>
	<tr><td class=question>Primary help needed:<span class=required-asterisk>*</span></td>
	<td class="answer"> 
	  <div class="form_field">
	    <select class="" id="work_type" name="work_type"><option value="">--Choose One--</option><option value="Flood">Flood</option><option value="Trees">Trees or Wind</option><option value="Other">Other</option><option value="Unknown">Unknown</option><option value="Goods or Services">Goods or Services</option><option value="Food">Food</option><option selected value="None">None</option></select>
	  </div>
	</td></tr>
	<tr><td class=question>Rent/Own/Public</td>
	<td class="answer"> 
	  <div class="form_field">
	    <select class="" id="rent_or_own" name="rent_or_own"><option value="">--Choose One--</option><option value="Rent">Rent</option><option value="Own">Own</option><option value="Public Land">Public Land</option><option value="Non-Profit">Non-Profit</option><option value="Business">Business</option></select>
	  </div>
	</td></tr>
	<tr><td class=question>Work without resident present?</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="work_without_resident" name="work_without_resident" type="checkbox" value="y">
	  </div>
	</td></tr>
	<tr><td class=question>Member of your organization:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="member_of_assessing_organization" name="member_of_assessing_organization" type="checkbox" value="y">
	  </div>
	</td></tr>
	<tr><td class=question>First Responder:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="first_responder" name="first_responder" type="checkbox" value="y">
	  </div>
	</td></tr>
	<tr><td class=question>Older than 60:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <input class="" id="disabled" name="disabled" type="checkbox" value="y">
	  </div>
	</td></tr>
	<tr><td class=question>Special needs:</td>
	<td class="answer"> 
	  <div class="form_field">
	    <textarea class="" id="special_needs" name="special_needs"></textarea>
	  </div>
	</td></tr>
	<tr><td class=question>Priority:</td>
	<td class="answer">
	<table>
	<tr><td>Low (5)</td>

	<td><input id="priority-0" name="priority" type="radio" value="5"></td>

	<td><input id="priority-1" name="priority" type="radio" value="4"></td>

	<td><input checked id="priority-2" name="priority" type="radio" value="3"></td>

	<td><input id="priority-3" name="priority" type="radio" value="2"></td>

	<td><input id="priority-4" name="priority" type="radio" value="1"></td>

	<td>(1) High</td></tr></table>

	</td></tr>

	</table>
	<br>

	"""
	
	html_button = '<input type=submit value="Submit request">'
	
	
	ignore_similar = """
	
<input type="checkbox" id="ignore_similar" name="ignore_similar">
<label for="ignore_similar">Ignore similar matches</label>
<br/>

"""
	final_form_html = primary_form_html + incident_form_html + ignore_similar + html_button
	parser = HtmlPropertiesParser()
	new_properties_list = parser.feed(incident_form_html)
	i = incident_csv_db.IncidentCSV(incident = event.key(), incident_csv = PROPERTIES_LIST)
	i.put()
	f = form_db.IncidentForm(incident = incident.key(), form_html = final_form_html, editable_form_html = incident_form_html)
	form_db.PutAndCache(f, cache_time)
	self.redirect("/admin?message=Form Added")

	return
	
class HtmlPropertiesParser(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        counter = 0
        if tag != "input":
	  return
	for name, value in attrs:
	  if name == "id":
	    PROPERTIES_LIST.append(value)
	    counter += 1
	    