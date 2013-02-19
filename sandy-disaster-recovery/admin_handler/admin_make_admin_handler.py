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

# Local libraries.
import base
import event_db
import site_db
import site_util
import cache

from datetime import datetime
import settings

from google.appengine.ext import db
import organization
import primary_contact_db
import random_password
import incident_admin_db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_incident_add_admin.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600

class AdminHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        global_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
            
        if global_admin == False:
            self.redirect("/")
            return
            
        org_id = self.request.get("organization")
        contact_id = self.request.get("contact")
        
        #try
        int_org_id = int(org_id)
        int_contact_id = int(contact_id)
        
        this_organization = organization.Organization.get_by_id(int_org_id)
        
        this_contact = primary_contact_db.Contact.get_by_id(int_contact_id)
        

        incident_admin = incident_admin_db.IncidentAdmin(
        incident = this_organization.incident.key(),
        contact = this_contact.key(),
        )
        cache.PutAndCache(incident_admin, 600)
        
        self.redirect("/admin?message=Admin Added")
        #contacts = None
        #order = None
        #order_string = ""
        #org_id = self.request.get("organization")
        #if self.request.get("order"):
            #order_kind = self.request.get("order")
            #order_string = " ORDER BY " + order_kind
            
        #query_string = "SELECT * FROM Contact" + order_string
        #contacts = db.GqlQuery(query_string)    
 
                    
        #self.response.out.write(template.render(
        #{
            #"contacts": contacts,
            #"display_contacts": True,
            #"global_admin": global_admin,
            #"org_id": org_id,
        #}))
        #return
