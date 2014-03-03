#
#
#
# DEPRECATED - put POST handler functions in handler classes
#
#
#
#
#
#
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
import json
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
template = jinja_environment.get_template('admin.html')
#CASE_LABELS = settings.CASE_LABELS
#COUNT = 26
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedPost(self, org, event):
        global_admin = False
        local_admin = False
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
            
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return

        if self.request.get("create_contact"):
            data = primary_contact_db.ContactFormFull(self.request.POST)
            if data.validate():
                organization_id = self.request.get("choose_organization")
                try:
                    id = int(organization_id)
                except:
                    return
                this_organization = organization.Organization.get_by_id(id)
                if not org.may_administer(this_organization):
                    self.abort(403)
                contact = primary_contact_db.Contact(
                    first_name=data.first_name.data,
                    last_name=data.last_name.data,
                    title=data.title.data,
                    phone=data.phone.data,
                    email=data.email.data,
                    is_primary=bool(data.is_primary.data),
                    organization=this_organization.key(),
                )
                primary_contact_db.PutAndCache(contact, ten_minutes)
                self.redirect("/admin-create-contact?selected_org=%s&message=Contact Created" % this_organization.key().id())
                return
            else:
                #query_string = "SELECT * FROM Event"
                #events_list = db.GqlQuery(query_string)
                suggested_password = random_password.generate_password()
                query_string = "SELECT * FROM Organization"
                organization_list = db.GqlQuery(query_string)
                
                
                self.response.out.write(template.render(
                {
                    "form": data,
                    "errors": data.errors,
                    "create_contact": True,
                    "organization_list": organization_list,
                }))
                return
            
        if self.request.get("create_admin"):
            data = organization.OrganizationAdminForm(self.request.POST)
            event_id = self.request.get("choose_event")
            try:
                id = int(event_id)
            except:
                return
            this_event = event_db.Event.get_by_id(id)
            if local_admin:
                if not this_event.key() == event.key():
                    self.redirect("/")
                    return
            
            if data.validate():
                    new_org = organization.Organization(name = data.name.data,
                        email = data.email.data,
                        phone = data.phone.data,
                        address = data.address.data,
                        city = data.city.data,
                        state = data.state.data,
                        zip_code = data.zip_code.data,
                        physical_presence = True,
                        number_volunteers = "0",
                        voad_member = False,
                        org_verified=True,
                        twitter = data.twitter.data,
                        url = data.url.data,
                        facebook = data.facebook.data,  
                        incidents = [this_event.key()],
                        password = self.request.get("password"),
                        is_active = True,
                        is_admin = True,
                    )

                    # set all phase fields true for admin
                    for phase_name in new_org.get_phase_boolean_names():
                        setattr(new_org, phase_name, True)

                    new_contact = primary_contact_db.Contact(
                        first_name=data.contact_first_name.data,
                        last_name=data.contact_last_name.data,
                        title=data.contact_title.data,
                        email=data.contact_email.data,
                        phone=data.contact_phone.data,
                        is_primary=True
                    )
                    
                    organization.PutAndCacheOrganizationAndContact(organization = new_org,
                        contact = new_contact,
                    )
                    self.redirect("/admin?message=Admin Created")
                    return
            else:
                # needs events lists, password, errors
                query_string = "SELECT * FROM Event"
                suggested_password = random_password.generate_password()
                self.response.out.write(template.render(
                {
                    "form": data,
                    "errors": data.errors,
                    "create_admin": True,
                    #"events_list": events_list,
                    "auto_password": suggested_password,
                }))
                return

        if self.request.get("delete_org_id"):
            # delete organization
            try:
                id = int(self.request.get("delete_org_id"))
                org_by_id = organization.Organization.get_by_id(id)
            except:
                self.abort(400)

            if not org.may_administer(org_by_id):
                self.abort(403)

            primary_contact_db.RemoveOrgFromContacts(org_by_id)
            db.delete(org_by_id)
            self.redirect("/admin")
            return

        if self.request.get("delete_contact_id"):
            # delete contact
            try:
                id = int(self.request.get("delete_contact_id"))
                contact_by_id = primary_contact_db.Contact.get_by_id(id)
            except:
                self.abort(400)

            if not org.may_administer(org_by_id):
                self.abort(403)

            db.delete(contact_by_id)
            self.redirect("/admin")
            return
            
        if self.request.get("verify_organization"):
            # verify organization
            try:
                id = int(self.request.get("verify_organization"))
                org_by_id = organization.Organization.get_by_id(id)
            except:
                self.abort(400)

            # check we are allowed
            if not org.may_administer(org_by_id):
                self.abort(403)

            # perform verification
            org_by_id.verify()

            # cache
            organization.PutAndCache(org_by_id, 600)
            self.redirect("/admin")
            return

        if self.request.get("save_org_id"):
            # save org (?)
            try:
                id = int(self.request.get("save_org_id"))
                org_by_id = organization.Organization.get_by_id(id)
            except:
                self.abort(400)

            if not org.may_administer(org_by_id):
                self.abort(403)

            org_by_id.org_verified = True
            organization.PutAndCache(org_by_id, 600)
            self.redirect("/admin")
            return


    def AuthenticatedGet(self, org, event):
        # get version dictionary params
        try:
            with open('version.json') as version_json_fd:
                version_d = json.load(version_json_fd)
        except:
            version_d = None

        # render response
        if org.name == GLOBAL_ADMIN_NAME:
            self.response.out.write(
                template.render({
                    "org": org,
                    "global_admin": True,
                    "message": self.request.get('message'),
                    "version_d": version_d,
                })
            )
            return
        elif org.is_admin == True:
            self.response.out.write(
                template.render({
                    "org": org,
                    "message": self.request.get('message'),
                    "version_d": version_d,
                })
            )
            return
        else:
            self.redirect("/")
