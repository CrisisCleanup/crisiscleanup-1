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
template = jinja_environment.get_template('admin_edit_organization.html')
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
                
            if local_admin:
                if not org.incident.key() == org_by_id.incident.key():
                    self.redirect("/")
                    return
            form = organization.OrganizationEditForm(None, org_by_id)
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
            

            
            
        #if org.name == GLOBAL_ADMIN_NAME:
            #if self.request.get("organization"):
                #try:
                    #id = int(self.request.get("organization"))
                #except:
                    #pass
                #org = organization.Organization.get_by_id(id)
                #form = organization.OrganizationEditForm(name = org.name,
                #password = org.password,
                #email = org.email,
                #phone = org.phone,
                #address= org.address,
                #city = org.city,
                #state = org.state,
                #zip_code = org.zip_code,
                #twitter = org.twitter,
                #facebook = org.facebook,
                #url = org.url,
                #physical_presence = org.physical_presence,
                #work_area = org.work_area,
                #number_volunteers = org.number_volunteers,
                #voad_member = org.voad_member,
                #voad_member_url = org.voad_member_url,
                #voad_referral = org.voad_referral,
                #canvass = org.canvass,
                #assessment = org.assessment,
                #clean_up = org.clean_up,
                #mold_abatement = org.mold_abatement,
                #rebuilding = org.rebuilding,
                #refurbishing = org.refurbishing,
                #org_verified = org.org_verified,
                #is_active = org.is_active,
                #)
                #self.response.out.write(template.render(
                #{
                    #"edit_org": True,
                    #"form": form,
                    #"org_id": org.key().id(),
                #}))
                #return
                
        #elif org.is_admin:
            #if self.request.get("organization"):
                #try:
                    #id = int(self.request.get("organization"))
                #except:
                    #pass
                #org_by_id = organization.Organization.get_by_id(id)
                #if not org.incident.key() == org_by_id.incident.key():
                    #self.redirect("/")
                    #return
                #form = organization.OrganizationEditForm(name = org.name,
                #password = org_by_id.password,
                #email = org_by_id.email,
                #phone = org_by_id.phone,
                #address= org_by_id.address,
                #city = org_by_id.city,
                #state = org_by_id.state,
                #zip_code = org_by_id.zip_code,
                #twitter = org_by_id.twitter,
                #facebook = org_by_id.facebook,
                #url = org_by_id.url,
                #physical_presence = org_by_id.physical_presence,
                #work_area = org_by_id.work_area,
                #number_volunteers = org_by_id.number_volunteers,
                #voad_member = org_by_id.voad_member,
                #voad_member_url = org_by_id.voad_member_url,
                #voad_referral = org_by_id.voad_referral,
                #canvass = org_by_id.canvass,
                #assessment = org_by_id.assessment,
                #clean_up = org_by_id.clean_up,
                #mold_abatement = org_by_id.mold_abatement,
                #rebuilding = org_by_id.rebuilding,
                #refurbishing = org_by_id.refurbishing,
                #org_verified = org_by_id.org_verified,
                #is_active = org_by_id.is_active,
                #)
                #self.response.out.write(template.render(
                #{
                    #"edit_org": True,
                    #"form": form,
                    #"org_id": org_by_id.key().id(),
                #}))
                #return
            
        #else:
            #self.redirect("/")
