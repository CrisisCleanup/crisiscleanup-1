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

# Local libraries.
import base
import event_db
import site_db
import site_util
import event_db
import new_incident_db
import json
import organization
jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('new_incident.html')


class OrganizationAjaxHandler(base.RequestHandler):
    def get(self):
        data = {}
        event = None
        for e in event_db.Event.gql("Where name = :1", self.request.get("event_name")):
            event = e
        for org in organization.Organization.gql(
            'Where incident = :1 and is_active = :2', event.key(), True):
            data[org.name] = org.name
        
        self.response.out.write(json.dumps(data))
 