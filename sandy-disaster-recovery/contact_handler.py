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
import site_db
import site_util
import event_db
import primary_contact_db
import organization
import key

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('contact.html')

class ContactHandler(base.RequestHandler):
    def get(self):
        logged_in = False
        org, event = key.CheckAuthorization(self.request)
        if org and key:
	  logged_in = True
        self.response.out.write(template.render(
        {
	  "logged_in": logged_in,
            #"form": form,
            #"events_list": events_list,
        }))

            
