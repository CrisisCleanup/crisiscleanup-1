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
from organization import Organization, CreateOrganizationForm
import primary_contact_db
import random_password

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_create_organization.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"


class AdminHandler(base.AuthenticatedHandler):

    def _get_events(self, org, global_admin, local_admin):
        if global_admin:
            query_string = "SELECT * FROM Event"
            return db.GqlQuery(query_string)
        
        if local_admin:
            query_string = "SELECT * FROM Event"
            events = db.GqlQuery(query_string)
            return [e for e in events if e.key() == org.incident.key()]

    def AuthenticatedGet(self, org, _):
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
            
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return

        # create form
        form = CreateOrganizationForm()
        events = self._get_events(org, global_admin, local_admin)
        form.incident.choices = [(str(event.key().id()), event.name) for event in events]
        form.password.data = random_password.generate_password()

        # render template
        self.response.out.write(template.render({
            "form": form,
            "global_admin": global_admin,
        }))

    def AuthenticatedPost(self, org, _):
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
            
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return

        # create form
        form = CreateOrganizationForm(self.request.POST)
        events = self._get_events(org, global_admin, local_admin)
        form.incident.choices = [(str(event.key().id()), event.name) for event in events]

        if form.validate() and not form.errors:
            # create new org
            event = event_db.Event.get_by_id(int(form.incident.data))
            new_org = Organization(
                name=form.name.data,
                incident=event,
            )
            del(form.incident)
            form.populate_obj(new_org)
            new_org.save()
            self.redirect('/admin-single-organization?organization=%d' % new_org.key().id())
        else:
            self.response.out.write(template.render({
                "form": form,
                "global_admin": global_admin,
            }))
