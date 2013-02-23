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
template = jinja_environment.get_template('organization_info.html')
display_all_template = jinja_environment.get_template('organizations_display_all.html')


class OrganizationInfoHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        name = self.request.get("organization")
        message = self.request.get("message")
        if not name:
            query_string = "SELECT * FROM Organization WHERE incident = :1 ORDER BY name"
            organization_list = db.GqlQuery(query_string, event.key())
            self.response.out.write(display_all_template.render({
                "org_query": organization_list,
                "message": message,
            }))
            return
        query_string = "SELECT * FROM Organization WHERE name = :1"
        organization_list = db.GqlQuery(query_string, name)
        for o in organization_list:
            id = o.key().id()
        
        org_by_id = organization.Organization.get_by_id(id)
        if not org_by_id.incident.key() == event.key():
            self.redirect("organization-info?message=The organization you are trying to view doesn't belong to the event that you are signed in to. If you think you are seeing this message in error, please contact your administrator.")
            return
        org_key = org_by_id.key()
        
        contact_query = None
        if org_by_id.is_admin:
            contact_query = db.GqlQuery("SELECT * From IncidentAdmin WHERE incident = :1", org_by_id.incident.key())
        else:
            contact_query = db.GqlQuery("SELECT * From Contact WHERE organization = :org_key", org_key = org_key)
        self.response.out.write(template.render(
        {
            "organization": org_by_id,
            "contacts": contact_query,
            "is_admin": org_by_id.is_admin,
            "message": message,
        }))
        return
        
        

            
