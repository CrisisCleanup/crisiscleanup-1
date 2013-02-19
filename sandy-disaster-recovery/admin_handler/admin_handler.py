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
                if local_admin:
                    if not this_organization.incident.key() == org.incident.key():
                        self.redirect("/")
                        return
                contact = primary_contact_db.Contact(first_name = data.first_name.data,
                    last_name = data.last_name.data,
                    phone = data.phone.data,
                    email = data.email.data,
                    is_primary = bool(data.is_primary.data),
                    organization = this_organization.key(),
                    )
                primary_contact_db.PutAndCache(contact, ten_minutes)
                self.redirect("/admin?message=Contact Created")
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
                        incident = this_event.key(),
                        password = self.request.get("password"),
                        is_active = True,
                        is_admin = True,
                    )

                    # set all phase fields true for admin
                    for phase_name in new_org.get_phase_boolean_names():
                        setattr(new_org, phase_name, True)

                    new_contact = primary_contact_db.Contact(first_name = data.contact_first_name.data,
                        last_name = data.contact_last_name.data,
                        email = data.contact_email.data,
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
                events_list = db.GqlQuery(query_string)
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
                
        if self.request.get("edit_contact_final"):
            try:
                id = int(self.request.get("edit_contact_final"))
            except:
                self.response.set_status(400)
                return
            org_id = None
            org_key = None
            
            # check to see if organization was edited
            if self.request.get("organization") != "None":
                try:
                    org_id = int(self.request.get("organization"))
                except:
                    self.response.set_status(400)
                    return
                org = organization.Organization.get_by_id(org_id)
                org_key = org.key()
                if local_admin:
                    if not org_key.incident.key() == org.incident.key():
                        self.redirect("/")
                        return
            ###########################
            this_contact = primary_contact_db.Contact.get(db.Key.from_path('Contact', id))
            if not this_contact.organization.incident.key() == org.incident.key():
                self.redirect("/")
                return
            data = primary_contact_db.ContactFormFull(self.request.POST)
            if data.validate():     

            
                contact = this_contact
                contact.first_name=data.first_name.data
                contact.last_name = data.last_name.data
                contact.phone=data.phone.data
                contact.email = data.email.data
                if org_key is not None:
                    contact.organization = org_key
                contact.is_primary=bool(data.is_primary.data)
                primary_contact_db.PutAndCache(contact, ten_minutes)
                self.redirect("/admin")
                return
            else:
                try:
                    id = int(self.request.get("edit_contact_final"))
                except:
                    self.response.set_status(400)
                    return
                contact = primary_contact_db.Contact.get_by_id(id)
                form = primary_contact_db.ContactFormFull(first_name = contact.first_name, last_name = contact.last_name, phone = contact.phone, email = contact.email, is_primary=int(contact.is_primary))
                self.response.out.write(template.render(
                {
                    "edit_contact_id": id,
                    "form": form,
                    "errors": data.errors
                }))
                return
                
        if self.request.get("create_org"):
            data = organization.OrganizationFormNoContact(self.request.POST)
            is_active_bool = False
            activate = self.request.get("is_active")
            if activate:
                is_active_bool = True
            
            if data.validate():
                logging.warn(data)
                new_org = organization.Organization(**data.data)
                organization.PutAndCache(new_org, ten_minutes)
            else:
                self.response.out.write(template.render(
                {
                    "form": data,
                    "errors": data.errors,
                    "create_org": True,
                }))
                return
            self.redirect("/admin")
            return
            
        if self.request.get("delete_org_id"):
            try:
                org_by_id = organization.Organization.get(db.Key.from_path('Organization', int(self.request.get("delete_org_id"))))
            except:
                self.response.set_status(400)
                return
            if local_admin:
                if not org_by_id.incident.key() == org.incident.key():
                    
                    self.redirect("/")
                    return
                
            primary_contact_db.RemoveOrgFromContacts(org_by_id)
            db.delete(org_by_id)
            self.redirect("/admin")
            return
            
        if self.request.get("activate_organization"):
            try:
                id = int(self.request.get("activate_organization"))
            except:
                self.response.set_status(400)
                return
            org_by_id = organization.Organization.get(db.Key.from_path('Organization', id))
            if local_admin:
                if not org_by_id.incident.key() == org.incident.key():
                    self.redirect("/")
                    return
                    
            org_by_id.org_verified=True
            org_by_id.is_active=True
            organization.PutAndCache(org_by_id, 600)
            self.redirect("/admin")
            return
        if self.request.get("save_org_id"):
            try:
                id = int(self.request.get("save_org_id"))
            except:
                self.response.set_status(400)
                return
            org_by_id = organization.Organization.get(db.Key.from_path('Organization', id))
            if local_admin:
                if not org_by_id.incident.key() == org.incident.key():
                    self.redirect("/")
                    return
                    
            org_by_id.org_verified=True
            organization.PutAndCache(org_by_id, 600)
            self.redirect("/admin")
            return
            
        if self.request.get("edit_org"):
            data = organization.OrganizationEditForm(self.request.POST)
            if data.validate():
                try:
                    id = int(self.request.get("edit_org"))
                except:
                    self.response.set_status(400)
                    return
                org_by_id = organization.Organization.get(db.Key.from_path('Organization', id))
                org_by_id.name = data.name.data
                org_by_id.org_verified = bool(data.org_verified.data)
                org_by_id.is_active = bool(data.is_active.data)
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
                org_by_id.number_volunteers = data.number_volunteers.data
                org_by_id.voad_member = bool(data.voad_member.data)
                org_by_id.voad_referral = data.voad_referral.data
                org_by_id.work_area = data.work_area.data
                org_by_id.voad_member_url = data.voad_member_url.data

                # phase fields
                for phase_field_name in org_by_id.get_phase_boolean_names():
                    setattr(org_by_id, phase_field_name, bool(data[phase_field_name].data))

                organization.PutAndCache(org_by_id, 600)
                self.redirect("/admin")
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
        if org.name == GLOBAL_ADMIN_NAME:
            self.response.out.write(template.render({"org": org, "global_admin": True}))
            return
        elif org.is_admin == True:
            self.response.out.write(template.render({"org": org}))
            return
        else:
            self.redirect("/")
