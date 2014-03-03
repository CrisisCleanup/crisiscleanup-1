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
import cache

from datetime import datetime
import settings

from google.appengine.ext import db
import organization
import primary_contact_db
import random_password

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('organization_edit_contacts.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600


class OrganizationEditContactsHandler(base.AuthenticatedHandler):

    def AuthenticatedPost(self, org, event):
        authenticated_org = org
        try:
            id = int(self.request.get("edit_contact_final"))
        except:
            self.response.set_status(400)
            return
        org_id = None
        org_key = None
        
        # check to see if organization was edited
        if self.request.get("organization") != "None":
            try:
                org_id = int(self.request.get("organization"))
            except:
                self.response.set_status(400)
                return
            org = organization.Organization.get_by_id(org_id)
            org_key = org.key()

        ###########################

        this_contact = primary_contact_db.Contact.get(db.Key.from_path('Contact', id))

        # abort if not authorised to update this contact: must match the authenticated org
        if this_contact.organization.key() != authenticated_org.key():
            self.abort(403)

        # abort if from another incident
        if event.key() not in (inc.key() for inc in this_contact.organization.incidents):
            self.abort(403)

        data = primary_contact_db.ContactFormFull(self.request.POST)
        if data.validate():     
            contact = this_contact
            contact.first_name=data.first_name.data
            contact.last_name = data.last_name.data
            contact.title = data.title.data
            contact.phone=data.phone.data
            contact.email = data.email.data
            if org_key is not None:
                contact.organization = org_key
            contact.is_primary=bool(data.is_primary.data)
            primary_contact_db.PutAndCache(contact, ten_minutes)
            self.redirect("/organization-settings?message=Edit complete. It may take a few moments to see changes.")
            return
        else:
            try:
                id = int(self.request.get("edit_contact_final"))
            except:
                self.response.set_status(400)
                return
            contact = primary_contact_db.Contact.get_by_id(id)
            form = primary_contact_db.ContactFormFull(
                first_name=contact.first_name,
                last_name=contact.last_name,
                title=contact.title,
                phone=contact.phone,
                email=contact.email,
                is_primary=int(contact.is_primary)
            )
            self.response.out.write(template.render(
            {
                "edit_contact_id": id,
                "form": form,
                "errors": data.errors
            }))
            return
        
    def AuthenticatedGet(self, authenticated_org, event):
        # get & check contact
        try:
            id = int(self.request.get("contact"))
            contact = primary_contact_db.Contact.get_by_id(id)
            if contact.organization.key() != authenticated_org.key():
                self.abort(403)
        except:
            self.abort(404)
       
        # get contact & org list
        query_string = "SELECT * FROM Organization WHERE name = :1"
        organization_list = db.GqlQuery(query_string, authenticated_org.name)

        # construct form
        form = primary_contact_db.ContactFormFull(None, contact)
        self.response.out.write(template.render({
            "organization_list": organization_list,
            "edit_contact_id": id,
            "form": form,
            "organization_name": contact.organization.name if contact.organization else None
        }))
