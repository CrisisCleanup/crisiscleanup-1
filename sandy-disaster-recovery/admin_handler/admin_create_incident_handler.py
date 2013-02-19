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
import organization
import random_password


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_create_incident.html')

CASE_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
GLOBAL_ADMIN_NAME = "Admin"


class AdminCreateIncidentHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return
        form = event_db.NewEventForm()
        query_string = "SELECT * FROM Event"
        events_list = db.GqlQuery(query_string)
        count = events_list.count()
        auto_password = random_password.generate_password()
        
        self.response.out.write(template.render(
        {
            "auto_password": auto_password,
            "form": form,
            "case_label": CASE_LABELS[count]
        }))
        
    def AuthenticatedPost(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return
        data = event_db.NewEventForm(self.request.POST)
        if not data.validate():
            query_string = "SELECT * FROM Event"
            events_list = db.GqlQuery(query_string)
            count = events_list.count()
            self.response.out.write(template.render(
            {
                "form": data,
                "errors": data.errors,
                "case_label": CASE_LABELS[count],
            }))
        else:
            query_string = "SELECT * FROM Event"
            events_list = db.GqlQuery(query_string)
            count = events_list.count()
            this_event = event_db.Event(name = data.name.data,
                                short_name = data.short_name.data,
                                case_label = CASE_LABELS[count],
                               )
            ten_minutes = 600
            cache.PutAndCache(this_event, ten_minutes)
            # create local admin
            
            new_admin = organization.Organization(name = "Local Admin - " + data.short_name.data,
            email = "",
            phone = "",
            address = "",
            city = "",
            state = "",
            zip_code = "",
            physical_presence = True,
            number_volunteers = "0",
            voad_member = False,
            org_verified=True,
            twitter = "",
            url = "",
            facebook = "",  
            incident = this_event.key(),
            password = self.request.get("password"),
            is_active = True,
            is_admin = True,
            )
            # set all phase fields true for admin
            for phase_name in new_admin.get_phase_boolean_names():
                setattr(new_admin, phase_name, True)
            organization.PutAndCache(new_admin, ten_minutes)
            self.redirect("/admin")
