#!/usr/bin/env python
#
# Copyright 2013 Chris Wood
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
import jinja2
import os
from google.appengine.ext import db
import wtforms.fields
import wtforms.form
import wtforms.validators


# Local libraries.
import base
import page_db
import organization
import event_db
import random_password
import generate_hash
import organization
import audit_db
import logging


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_generate_new_password.html')
post_template = jinja_environment.get_template('admin_view_new_password.html')

GLOBAL_ADMIN_NAME = "Admin"

def GetOrganizationForm(post_data):
  e = event_db.Event(name = "Test Incident",
  case_label = "B",
  counties = ["Kings"])
  query_string = "SELECT * FROM Organization WHERE is_active = True ORDER BY name"
  organizations = db.GqlQuery(query_string)
  events = event_db.GetAllCached()
  events = db.GqlQuery("SELECT * From Event ORDER BY created_date DESC")
  event_key = None
  if events.count() == 0:
    logging.warning("Initialize called")
    e = event_db.Event(name = "North Central Victorian Floods",
                       case_label = "A",
                       short_name = "ncv_floods")
    e.put()
    event_key = e.key()
    # TODO(Jeremy): This could be dangerous if we reset events.
    for s in site_db.Site.all().run(batch_size = 1000):
      event_db.AddSiteToEvent(s, e.key().id(), force = True)
    events = [e]

  if organizations.count() == 0:
    # init: populate the database with Admin user
    admin_org = organization.Organization(
        name="Admin",
        password="temporary_password",
        org_verified=True,
        is_active=True,
        is_admin=True,
        incidents=[event_key]
    )
    admin_org.put()
    admin_contact = primary_contact_db.Contact(
        first_name="Admin",
        last_name="Admin",
        title="Admin",
        phone="1234",
        email="admin@admin.admin",
        organization=admin_org,
        is_primary=True
    )
    admin_contact.put()
    organizations = db.GqlQuery("SELECT * FROM Organization WHERE is_active = True ORDER BY name")

  class OrganizationForm(wtforms.form.Form):
    event = wtforms.fields.SelectField(
        'Work Event',
        choices = [(e.name, e.name) for e in events],
        validators = [wtforms.validators.required()])
    password = wtforms.fields.PasswordField(
        'Password',
        validators = [ wtforms.validators.required() ])
  form = OrganizationForm(post_data)
  return form


class AdminGenerateNewPassword(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        global_admin = (org.name == GLOBAL_ADMIN_NAME)
        if not global_admin:
            self.redirect("/")
            return
        template_params = page_db.get_page_block_dict()
        template_params.update({
          "form" : GetOrganizationForm(self.request.POST),
          "destination" : self.request.get('destination', default_value='/'),
          "page" : "/admin-generate-new-password",
          "error_message": self.request.get("error_message"),
          "initial_event_name": self.request.get("initial_event_name", ""),
        })
        self.response.out.write(template.render(template_params))

        
    def AuthenticatedPost(self, org, event):
        name = self.request.get("name")
        event_name = self.request.get("event")
        logging.info("new password")
        logging.info(name)
        logging.info(event_name)
        password = self.request.get("password")
        if self.request.get("accept") == "true":
          event = event_db.Event.all().filter("name =", event_name).get()
          org = organization.Organization.all().filter("name =", name).filter("incidents =", event.key()).get()
          password_hash = generate_hash.recursive_hash(password)
          if org:
            if password_hash in org._password_hash_list:
              self.rediect("/admin?message=That password already exists for that organization")
              return
            org._password_hash_list.append(password_hash)
            org._password_hash_list = list(set(org._password_hash_list))
            organization.PutAndCache(org)
            audit = audit_db.new_password(org, password_hash)
            url = "/admin?message=New password added to " + name + " working on " + event_name
            self.redirect(url)
            return
          else:
            url = "/admin-generate-new-password?error_message=Could not find " + name + "for: " event_name
            self.redirect(url)

        password = random_password.generate_password()
        template_params = page_db.get_page_block_dict()
        template_params.update({
          "password": password,
          "name": name,
          "event": event
        })
        self.response.out.write(post_template.render(template_params))
