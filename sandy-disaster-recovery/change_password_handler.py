#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
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
import Cookie
import datetime
import jinja2
import os
import urllib
from google.appengine.ext import db
import random
import string
import wtforms.fields
import wtforms.form
import wtforms.validators
import logging
import time

# Local libraries.
import base
import event_db
import key
import organization
import site_db
import page_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('change_password.html')
GLOBAL_ADMIN_NAME = "Admin"


def GetOrganizationForm(post_data):
  e = event_db.Event(name = "Test Incident",
  case_label = "B",
  counties = ["Kings"])
  query_string = "SELECT * FROM Organization WHERE is_active = True ORDER BY name"
  organizations = db.GqlQuery(query_string)
  events = event_db.GetAllCached()
  events = db.GqlQuery("SELECT * From Event ORDER BY created_date DESC")
  dirty = False
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
    #time.sleep(5)
    # This is to initially populate the database the first time.
    # TODO(oryol): Add a regular Google login-authenticated handler
    # to add users and passwords, whitelisted to the set of e-mail
    # addresses we want to allow.
    default = organization.Organization(name = "Admin", password = "temporary_password", org_verified=True, is_active=True, is_admin=True, incident = event_key)
    default.put()
    organizations = db.GqlQuery("SELECT * FROM Organization WHERE is_active = True ORDER BY name")# WHERE organization = :1 LIMIT 1", obj.key())
  elif organizations.count() >= 2:
    modified = []
    for o in organizations:
      #if o.name == "Administrator":
        #pass
        ##o.delete()
      #else:
      modified.append(o)
    organizations = modified


  #organizations.sort(key=lambda org: org.name)
  #events.sort(key=lambda event: event.name)
  
  class OrganizationForm(wtforms.form.Form):
    #name = wtforms.fields.SelectField(
        #'Name',
        #choices = [(o.name, o.name) for o in organizations],
        #validators = [wtforms.validators.required()])
    event = wtforms.fields.SelectField(
        'Work Event',
        choices = [(e.name, e.name) for e in events],
        validators = [wtforms.validators.required()])
    password = wtforms.fields.PasswordField(
        'Password',
        validators = [ wtforms.validators.required() ])
  form = OrganizationForm(post_data)
  return form

class ChangePasswordHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    if org.name != GLOBAL_ADMIN_NAME:
      self.redirect("/authentication")
      return

    template_params = page_db.get_page_block_dict()
    template_params.update({
      "form" : GetOrganizationForm(self.request.POST),
      "destination" : self.request.get('destination', default_value='/'),
      "page" : "/authentication",
      "error_message": self.request.get("error_message")
    })
    self.response.out.write(template.render(template_params))

  def AuthenticatedPost(self, org, event):
    if org.name != GLOBAL_ADMIN_NAME:
      self.redirect("/authentication")
      return
    event = self.request.get("event")
    name = self.request.get("name")
    password = self.request.get("password")
    new_password = self.request.get("new_password")
    confirm_password = self.request.get("confirm_password")
    if new_password != confirm_password:
      self.redirect("/change_password?error_message=New passwords don't match")
      return
    org = None
    e = event_db.Event.all()
    e.filter("name =", event)
    events = e.run()
    i = None
    for incident in events:
      i = incident
    
    q = organization.Organization.all()
    q.filter('name =', name)
    q.filter('incident =', i.key())
    q.filter('password =', password)
    orgs = q.run()
    for o in orgs:
      org = o
    if org == None:
      self.redirect("/change_password?error_message=Incorrect Organization and Passcode Combination")
      return
    else:
      org.password = new_password
      org.put()
      self.redirect("/change_password?error_message=Password Successfully Updated")

    # get event, org, password, new_password
    # change org to have new_password
    # redirect
    # if event/org/pwd don't line up, then reidrect with an error message