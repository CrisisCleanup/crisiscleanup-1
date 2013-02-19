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
template = jinja_environment.get_template('organization_edit_info.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
ten_minutes = 600

class OrganizationEditInfoHandler(base.AuthenticatedHandler):
    def AuthenticatedPost(self, org, event):
        data = organization.OrganizationInfoEditForm(self.request.POST)
        if data.validate():
            try:
                id = int(self.request.get("edit_org"))
            except:
                self.response.set_status(400)
                return
            org_by_id = organization.Organization.get(db.Key.from_path('Organization', id))
            org_by_id.name = data.name.data
            #org_by_id.org_verified = bool(data.org_verified.data)
            #org_by_id.is_active = bool(data.is_active.data)
            org_by_id.email = data.email.data
            org_by_id.phone = data.phone.data
            org_by_id.address = data.address.data
            org_by_id.city = data.city.data
            org_by_id.state = data.state.data
            org_by_id.zip_code = data.zip_code.data
            org_by_id.twitter = data.twitter.data
            org_by_id.facebook = data.facebook.data
            org_by_id.url = data.url.data
            org_by_id.physical_presence = bool(data.physical_presence.data)
            org_by_id.voad_membership = bool(data.voad_member.data)
            org_by_id.voad_referral = data.voad_referral.data
            org_by_id.canvassing = bool(data.canvass.data)
            org_by_id.assessment = bool(data.assessment.data)
            org_by_id.clean_up = bool(data.clean_up.data)
            org_by_id.mold_abatement = bool(data.mold_abatement.data)
            org_by_id.refurbishing = bool(data.refurbishing.data)
            org_by_id.rebuilding = bool(data.rebuilding.data)
            org_by_id.number_volunteers = data.number_volunteers.data
            
            organization.PutAndCache(org_by_id, 600)
            self.redirect("/organization-settings")
            return
        else:
            self.response.out.write(template.render(
            {
                "edit_org": True,
                "form": data,
                "errors": data.errors,
                "org_id": int(self.request.get("edit_org")),
            }))
            return
        
        
        
    def AuthenticatedGet(self, org, event):
        global_admin = False
        local_admin = False
        if self.request.get("organization"):
            try:
                id = int(self.request.get("organization"))
            except:
                self.redirect("/admin")
                return
                
            org_by_id = organization.Organization.get_by_id(id)
                
            if local_admin:
                if not org.incident.key() == org_by_id.incident.key():
                    self.redirect("/")
                    return
                    
            #print org_by_id.number_volunteers
            form = organization.OrganizationInfoEditForm(name = org_by_id.name,
            password = org_by_id.password,
            email = org_by_id.email,
            phone = org_by_id.phone,
            address= org_by_id.address,
            city = org_by_id.city,
            state = org_by_id.state,
            zip_code = org_by_id.zip_code,
            twitter = org_by_id.twitter,
            facebook = org_by_id.facebook,
            url = org_by_id.url,
            physical_presence = org_by_id.physical_presence,
            work_area = org_by_id.work_area,
            number_volunteers = org_by_id.number_volunteers,
            voad_member = org_by_id.voad_membership,
            voad_member_url = org_by_id.voad_member_url,
            voad_referral = org_by_id.voad_referral,
            canvass = org_by_id.canvassing,
            assessment = org_by_id.assessment,
            clean_up = org_by_id.clean_up,
            mold_abatement = org_by_id.mold_abatement,
            rebuilding = org_by_id.rebuilding,
            refurbishing = org_by_id.refurbishing,
            org_verified = org_by_id.org_verified,
            is_active = org_by_id.is_active,
            )
            self.response.out.write(template.render(
            {
                "edit_org": True,
                "form": form,
                "org_id": org_by_id.key().id(),
                "global_admin": global_admin,
            }))
            return
        else:
            self.redirect("/admin")
            

            