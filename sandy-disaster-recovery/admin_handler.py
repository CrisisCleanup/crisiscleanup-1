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
        if not org.name == GLOBAL_ADMIN_NAME:
            self.response.set_status(401)            
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
                contact = primary_contact_db.Contact(first_name = data.first_name.data,
                    last_name = data.last_name.data,
                    phone = data.phone.data,
                    email = data.phone.data,
                    is_primary = bool(data.is_primary.data),
                    organization = this_organization.key(),
                    )
                primary_contact_db.PutAndCache(contact, ten_minutes)
                self.redirect("/admin?message=Contact Created")
                return
            else:
                events_list = event_db.GetAllCached()
                suggested_password = random_password.generate_password()
                organization_list = organization.GetAllCached()
                
                
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
                        voad_membership = False,
                        canvassing = True,
                        assessment = True,
                        clean_up = True,
                        mold_abatement = True,
                        rebuilding = True,
                        org_verified=True,
                        twitter = data.twitter.data,
                        url = data.url.data,
                        facebook = data.facebook.data,  
                        incident = this_event.key(),
                        password = self.request.get("password"),
                        is_active = True,
                        is_admin = True,
                    )

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
                events_list = event_db.GetAllCached()
                suggested_password = random_password.generate_password()
                self.response.out.write(template.render(
                {
                    "form": data,
                    "errors": data.errors,
                    "create_admin": True,
                    "events_list": events_list,
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
            ###########################
                
            data = primary_contact_db.ContactFormFull(self.request.POST)
            if data.validate():
                contact = primary_contact_db.Contact.get(db.Key.from_path('Contact', id))
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
                
        if self.request.get("edit_contact_id"):
            try:
                id = int(self.request.get("edit_contact_id"))
            except:
                self.response.set_status(400)
                return
            organization_list = organization.GetAllCached()
            contact = primary_contact_db.Contact.get_by_id(id)
            form = primary_contact_db.ContactFormFull(first_name = contact.first_name, last_name=contact.last_name, phone = contact.phone, email = contact.email, is_primary=int(contact.is_primary))
            organization_name = None
            if contact.organization:
                organization_name = contact.organization.name
            self.response.out.write(template.render(
            {
                "organization_list": organization_list,
                "edit_contact_id": id,
                "form": form,
                "organization_name": organization_name
            }))
            return
                 
        if self.request.get("edit_org_id"):
            try:
                id = int(self.request.get("edit_org_id"))
            except:
                self.response.set_status(400)
                return
            org = organization.Organization.get_by_id(id)
            form = organization.OrganizationEditForm(name = org.name,
                email = org.email,
                phone = org.phone,
                address= org.address,
                city = org.city,
                state = org.state,
                zip_code = org.zip_code,
                twitter = org.twitter,
                facebook = org.facebook,
                url = org.url,
                physical_presence = org.physical_presence,
                work_area = org.work_area,
                number_volunteers = org.number_volunteers,
                voad_member = org.voad_membership,
                voad_member_url = org.voad_member_url,
                voad_referral = org.voad_referral,
                canvass = org.canvassing,
                assessment = org.assessment,
                clean_up = org.clean_up,
                mold_abatement = org.mold_abatement,
                rebuilding = org.rebuilding,
                refurbishing = org.refurbishing,
                org_verified = org.org_verified,
                is_active = org.is_active,
                )
            self.response.out.write(template.render(
            {
                "edit_org": True,
                "form": form,
                "org_id": org.key().id(),
            }))
            return
                        
        if self.request.get("create_org"):
            data = organization.OrganizationFormNoContact(self.request.POST)
            if data.validate():
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
                    org_verified=True,
                    twitter = data.twitter.data,
                    url = data.url.data,
                    voad_referral = data.voad_referral.data,
                    work_area = data.work_area.data,
                    voad_member_url = data.voad_member_url.data,
                    facebook = data.facebook.data,  
                    incident = event.key(),
                    password = self.request.get("password")
                )
                organization.PutAndCache(new_org, ten_minutes)
            else:
                events_list = event_db.GetAllCached()
                self.response.out.write(template.render(
                {
                    "form": data,
                    "errors": data.errors,
                    "events_list": events_list,
                    "create_org": True,
                }))
                return
            self.redirect("/admin")
            return
            
        if self.request.get("delete_org_id"):
            try:
                org = organization.Organization.get(db.Key.from_path('Organization', int(self.request.get("delete_org_id"))))
            except:
                self.response.set_status(400)
                return
            primary_contact_db.RemoveOrgFromContacts(org)
            db.delete(org)
            self.redirect("/admin")
            return
            
        if self.request.get("save_org_id"):
            try:
                id = int(self.request.get("save_org_id"))
            except:
                self.response.set_status(400)
                return
            org = organization.Organization.get(db.Key.from_path('Organization', id))
            org.org_verified=True
            organization.PutAndCache(org, 600)
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
            
                org = organization.Organization.get(db.Key.from_path('Organization', id))
                org.name = data.name.data
                org.org_verified = bool(data.org_verified.data)
                org.is_active = bool(data.is_active.data)
                org.email = data.email.data
                org.phone = data.phone.data
                org.address = data.address.data
                org.city = data.city.data
                org.state = data.state.data
                org.zip_code = data.zip_code.data
                org.twitter = data.twitter.data
                org.facebook = data.facebook.data
                org.url = data.url.data
                org.physical_presence = bool(data.physical_presence.data)
                org.voad_membership = bool(data.voad_member.data)
                org.voad_referral = data.voad_referral.data
                org.canvassing = bool(data.canvass.data)
                org.assessment = bool(data.assessment.data)
                org.clean_up = bool(data.clean_up.data)
                org.mold_abatement = bool(data.mold_abatement.data)
                org.refurbishing = bool(data.refurbishing.data)
                org.rebuilding = bool(data.rebuilding.data)
                organization.PutAndCache(org, 600)
                self.redirect("/admin")
                return
            else:
                events_list = event_db.GetAllCached()
                self.response.out.write(template.render(
                {
                    "edit_org": True,
                    "form": data,
                    "errors": data.errors,
                    "org_id": int(self.request.get("edit_org")),
                }))
                return
            
        
    def AuthenticatedGet(self, org, event):
        if not org.name == GLOBAL_ADMIN_NAME:
            return
          
        if self.request.get("display_contacts"):
            contacts = db.GqlQuery("SELECT * From Contact")
            self.response.out.write(template.render(
            {
                "contacts": contacts,
                "display_contacts": True,
            }))
            return
            
        if self.request.get("create_contact"):
            form = primary_contact_db.ContactFormFull()
            organization_list = db.GqlQuery("SELECT * From Organization WHERE org_verified = :1", True)
            self.response.out.write(template.render(
            {
                "form": form,
                "organization_list": organization_list,
                "create_contact": True,
            }))
            return
            
        if self.request.get("create_admin"):
            form = organization.OrganizationAdminForm()
            events_list = event_db.GetAllCached()
            suggested_password = random_password.generate_password()
            
            self.response.out.write(template.render(
            {
                "create_admin": True,
                "form": form,
                "events_list": events_list,
                "auto_password": suggested_password,
            }))
            return
            
        if self.request.get("message"):
            self.response.out.write(template.render(
            {
                "message": self.request.get("message"),
            }))
            return
        if self.request.get("contact"):
            try:
                id = int(self.request.get("contact"))
            except:
                self.response.set_status(400)
                return
            contact = primary_contact_db.Contact.get_by_id(id)
            self.response.out.write(template.render(
            {
                "single_contact": contact,
            }))
            return

        if self.request.get("org"):
            try:
                id = int(self.request.get("org"))
            except:
                self.response.set_status(400)
                return
            obj = cache.GetCachedById(organization.Organization, ten_minutes, id)
            contacts = db.GqlQuery("SELECT * FROM Contact WHERE organization = :1", obj.key())
            suggested_password = random_password.generate_password()
            self.response.out.write(template.render(
            {
                "new_organization": obj,
                "contacts": contacts,
                "suggested_password": suggested_password,
            }))
            return
            
        if self.request.get("inactive_orgs"):
            query_string = "SELECT * FROM Organization WHERE is_active = False"
            query = db.GqlQuery(query_string)
            self.response.out.write(template.render(
            {
                "org_query": query,
                "url": "/admin?org=",
            }))
            return
            
        if self.request.get("all_orgs"):
            query_string = "SELECT * FROM Organization"
            query = db.GqlQuery(query_string)
            self.response.out.write(template.render(
            {
                "org_query": query,
                "url": "/admin?org=",
            }))
            return
            
        if self.request.get("org_requests"):
            query_string = "SELECT * FROM Organization WHERE org_verified = False"
            query = db.GqlQuery(query_string)
            self.response.out.write(template.render(
            {
                "org_query": query,
                "url": "/admin?new_organization=",
            }))
            return
        
        if self.request.get("new_organization"):
            try:
                id = int(self.request.get("new_organization"))
            except:
                self.response.set_status(400)
                return
            obj = cache.GetCachedById(organization.Organization, ten_minutes, id)
            query = db.GqlQuery("SELECT * FROM Contact WHERE organization = :1 LIMIT 1", obj.key())
            contact_id = None
            contact = None
            for q in query:
                contact_id = q.key().id()
            if contact_id:
                contact = primary_contact_db.Contact.get_by_id(contact_id)    
            suggested_password = random_password.generate_password()
            
            self.response.out.write(template.render(
            {
                "form": True,
                "new_organization": obj,
                "contact": contact,
                "suggested_password": suggested_password,
            }))
            return

        if self.request.get("create_org"):
            form = organization.OrganizationFormNoContact()
            events_list = event_db.GetAllCached()
            auto_password = random_password.generate_password()
            self.response.out.write(template.render(
            {
                "form": form,
                "events_list": events_list,
                "create_org": True,
                "auto_password": auto_password,
            }))
            return
        self.response.out.write(template.render({}))
        return