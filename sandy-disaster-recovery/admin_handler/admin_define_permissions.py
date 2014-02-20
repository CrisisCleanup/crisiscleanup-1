#!/usr/bin/env python
#
# Copyright 2014 Andy Gimma
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

# Local libraries.
import base
import event_db
import cache
import incident_csv_db
from datetime import datetime
import settings
import incident_permissions_db

from google.appengine.ext import db


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_define_permissions.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600

class AdminDefinePermissions(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        query = event_db.Event.all()
        events = query.fetch(100)
        short_name = self.request.get("short_name")
        this_event = None
        form_params_list = []
        permissions_list = []
        permission_type = self.request.get("permission_type")
        current_redactions = None
        
        if short_name:
	  if permission_type:
	    event_query = event_db.Event.all()
	    event_query.filter("short_name =", short_name)
	    this_event = event_query.get()
	    
	    
	    incident_csv_query = incident_csv_db.IncidentCSV.all()
	    incident_csv_query.filter("incident =", this_event.key())
	    this_incident = incident_csv_query.get()
	    if this_incident:
	      form_params_list = this_incident.incident_csv
	      
	      i_ps = incident_permissions_db.IncidentPermissions.all()
	      i_ps.filter("incident =", this_event.key())
	      this_i_ps = i_ps.get()
	      if this_i_ps:
		if permission_type == "Situational Awareness":
		  current_redactions = this_i_ps.situational_awareness_redactions
		else:
		  current_redactions = this_i_ps.partial_access_redactions
	  else:
	    permissions_list = ["Partial Access", "Situational Awareness"]
	    
	
        self.response.out.write(template.render({
	  "events": events,
	  "short_name": short_name,
	  "this_event": this_event,
	  "form_params_list": form_params_list,
	  "permission_type": permission_type,
	  "permissions_list": permissions_list,
	  "current_redactions": current_redactions
            
        }))
	
    def AuthenticatedPost(self, org, event):
	#raise Exception(self.request)
        # get all requests
        # save as array to incident_permissions_db
        post_request = self.request.POST
        array_list = []
	for param in post_request:
	    if param != "short_name" and param != "permission_type":
		array_list.append(param)
	    
        short_name = self.request.get("short_name")
        permission_type = self.request.get("permission_type")
	event_query = event_db.Event.all()
	event_query.filter("short_name =", short_name)
	this_event = event_query.get()
	
	i_ps = incident_permissions_db.IncidentPermissions.all()
	i_ps.filter("incident =", this_event.key())
	this_i_ps = i_ps.get()
	if this_i_ps:
	  if permission_type == "Situational Awareness":
	    this_i_ps.situational_awareness_redactions = array_list
	  else:
	    this_i_ps.partial_access_redactions = array_list
	  this_i_ps.put()
	else:
	  i_p = incident_permissions_db.IncidentPermissions(incident=this_event.key())
	  if permission_type == "Situational Awareness":
	    i_p.situational_awareness_redactions = array_list
	  else:
	    i_p.partial_access_redactions = array_list
	    i_p.situational_awareness_redactions = array_list
	  i_p.put()

	self.redirect(str("admin-define-permissions?short_name=" + short_name + "&permission_type=" + permission_type))