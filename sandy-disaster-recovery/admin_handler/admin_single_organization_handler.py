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

from datetime import datetime
import settings

from google.appengine.ext import db
import organization
import primary_contact_db
import random_password

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_single_organization.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600

class AdminHandler(base.AuthenticatedHandler):
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
            
            
        if self.request.get("organization"):
            try:
                id = int(self.request.get("organization"))
            except:
                self.redirect("/admin")
                return
            
        
            org_by_id = organization.Organization.get_by_id(id)
            org_key = org_by_id.key()
            if local_admin:
                if not org_by_id.incident.key() == org.incident.key():
                    self.redirect("/admin")
                    return
            contact_query = None
            if org_by_id.is_admin:
                contact_query = db.GqlQuery("SELECT * From IncidentAdmin WHERE incident = :1", org_by_id.incident.key())
            else:
                contact_query = db.GqlQuery("SELECT * From Contact WHERE organization = :org_key", org_key = org_key)
            self.response.out.write(template.render(
            {
                "organization": org_by_id,
                "contacts": contact_query,
                "global_admin": global_admin,
                "is_admin": org_by_id.is_admin,
            }))
            return
        else:
            self.redirect("/admin")
            
