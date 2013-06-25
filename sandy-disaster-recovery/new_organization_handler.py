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

from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField

# System libraries.
import cgi
import jinja2
import logging
import os
import urllib2
import wtforms.validators
import cache
from google.appengine.ext import db


# Local libraries.
import base
import event_db
import primary_contact_db
import organization
import key
import page_db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('new_new_organization.html')

class NewOrganizationHandler(base.RequestHandler):
    def get(self):
	logged_in = False
        org, event = key.CheckAuthorization(self.request)
        if org and key:
	  logged_in = True
        form = organization.OrganizationForm()
        #events_list = event_db.GetAllCached()
        events_list = db.GqlQuery("SELECT * FROM Event ORDER BY created_date DESC")

        template_params = page_db.get_page_block_dict()
        template_params.update({
	    "logged_in": logged_in,
            "events_list": events_list,
        })
        self.response.out.write(template.render(template_params))
        
    def post(self):
        choose_event = self.request.get("choose_event")
        data = organization.OrganizationForm(self.request.POST)
        org = organization.Organization(name= self.request.get("name"), is_active=False, org_verified=False)
        contact_properties_list = ["first_name", "last_name", "personal_phone", "personal_email"]
        boolean_properties_list = ["publish", "physical_presence", "appropriate_work", "voad_member"]
	for k, v in self.request.POST.iteritems():
	  if k not in contact_properties_list:
	    if k == "choose_event":
	      chosen_event = event_db.Event.get_by_id(int(v))
	      setattr(org, "incident", chosen_event.key())
	    elif k in boolean_properties_list:
	      setattr(org, k, bool(v))

	    else:
	      setattr(org, k, v)
      
	new_contact = primary_contact_db.Contact(first_name = self.request.get("first_name"),
			    last_name = self.request.get("last_name"),
			    email = self.request.get("personal_email"),
			    phone=self.request.get("personal_phone"),
			    is_primary=True)
			    
	organization.PutAndCacheOrganizationAndContact(organization = org,
			    contact = new_contact,
			    )
			    
	self.redirect("/welcome")
            
