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

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('organization_add_contacts.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600

class OrganizationAddContactsHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        form = primary_contact_db.ContactFormFull()
        organization_list = None
        query_string = "SELECT * FROM Organization WHERE name = :1"
        organization_list = db.GqlQuery(query_string, org.name)
                    
            
        self.response.out.write(template.render(
        {
            "form": form,
            "organization_list": organization_list,
            "create_contact": True,
        }))
        return
        
    def AuthenticatedPost(self, org, event):
        data = primary_contact_db.ContactFormFull(self.request.POST)
        if data.validate():
            organization_id = self.request.get("choose_organization")
            try:
                id = int(organization_id)
            except:
                return
            this_organization = organization.Organization.get_by_id(id)
            contact = primary_contact_db.Contact(first_name = data.first_name.data,
                last_name = data.last_name.data,
                phone = data.phone.data,
                email = data.email.data,
                is_primary = bool(data.is_primary.data),
                organization = this_organization.key(),
                )
            primary_contact_db.PutAndCache(contact, ten_minutes)
            self.redirect("/organization-settings?message=Contact created. It may take a few moments for the contact to show up on your list.")
            return
        else:
            suggested_password = random_password.generate_password()
            query_string = "SELECT * FROM Organization"
            organization_list = db.GqlQuery(query_string)
            
            
            self.response.out.write(template.render(
            {
                "form": data,
                "errors": data.errors,
                "create_contact": True,
                "organization_list": organization_list,
            }))
            return
            