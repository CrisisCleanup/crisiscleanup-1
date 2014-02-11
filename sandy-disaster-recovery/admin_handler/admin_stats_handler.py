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
template = jinja_environment.get_template('admin_stats.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600


class AdminStatsHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
	SANDY_TOTAL_SITES = 0
	MOORE_TOTAL_SITES = 0
	HATTIESBURG_TOTAL_SITES = 0
	GORDON_BARTOW_TOTAL_SITES = 0
        global_admin = False
        local_admin = False
	if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return
        
	q = event_db.Event.all()
	query = q.fetch(1000)
	for q in query:
	  if q.short_name == "sandy":
	    SANDY_TOTAL_SITES = q.num_sites
	  if q.short_name == "moore":
	    MOORE_TOTAL_SITES = q.num_sites
	  if q.short_name == "derechos":
	    HATTIESBURG_TOTAL_SITES = q.num_sites
	  if q.short_name == "gordon-barto-tornado":
	    GORDON_BARTOW_TOTAL_SITES = q.num_sites
	
        self.response.out.write(template.render(
        {
            "global_admin": global_admin,
            "SANDY_TOTAL_SITES": SANDY_TOTAL_SITES,
            "MOORE_TOTAL_SITES": MOORE_TOTAL_SITES,
            "HATTIESBURG_TOTAL_SITES": HATTIESBURG_TOTAL_SITES,
            "GORDON_BARTOW_TOTAL_SITES": GORDON_BARTOW_TOTAL_SITES,
            "TOTAL_SITES": SANDY_TOTAL_SITES + MOORE_TOTAL_SITES + HATTIESBURG_TOTAL_SITES + GORDON_BARTOW_TOTAL_SITES
        }))
        return
