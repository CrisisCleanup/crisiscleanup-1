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

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('new_organization.html')

class NewOrganizationHandler(base.RequestHandler):
    def get(self):
        form = organization.OrganizationForm()
        #events_list = event_db.GetAllCached()
        events_list = db.GqlQuery("SELECT * FROM Event ORDER BY created_date DESC")
        self.response.out.write(template.render(
        {
            "form": form,
            "events_list": events_list,
        }))
        
    def post(self):
        choose_event = self.request.get("choose_event")
        data = organization.OrganizationForm(self.request.POST)
        if not data.validate():
            events_list = event_db.GetAllCached()
            self.response.out.write(template.render(
            {
                "form": data,
                "errors": data.errors,
                "events_list": events_list,
            }))
        else:
            event_id = data.choose_event.data
            event = event_db.GetEventFromParam(event_id)
            new_org = organization.Organization(name = data.name.data,
                                email = data.email.data,
                                phone = data.phone.data,
                                address = data.address.data,
                                city = data.city.data,
                                state = data.state.data,
                                zip_code = data.zip_code.data,
                                physical_presence = bool(data.physical_presence.data),
                                number_volunteers = data.number_volunteers.data,
                                voad_member = bool(data.voad_member.data),
                                voad_membership = bool(data.voad_membership.data),
                                canvassing = bool(data.canvass.data),
                                assessment = bool(data.assessment.data),
                                clean_up = bool(data.clean_up.data),
                                mold_abatement = bool(data.mold_abatement.data),
                                rebuilding = bool(data.rebuilding.data),
                                refurbishing = bool(data.refurbishing.data),
                                choose_event = event,
                                org_verified=bool(0),
                                twitter = data.twitter.data,
                                url = data.url.data,
                                voad_referral = data.voad_referral.data,
                                work_area = data.work_area.data,
                                voad_member_url = data.voad_member_url.data,
                                facebook = data.facebook.data,  
                                incident = event.key(),
                                )
                                
            new_contact = primary_contact_db.Contact(first_name = data.contact_first_name.data,
                                last_name = data.contact_last_name.data,
                                email = data.contact_email.data,
                                phone=data.contact_phone.data,
                                is_primary=True)
                                
            organization.PutAndCacheOrganizationAndContact(organization = new_org,
                                contact = new_contact,
                                )
                                
            self.redirect("/welcome")
            