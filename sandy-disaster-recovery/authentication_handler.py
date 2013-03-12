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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('authentication.html')

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
    e = event_db.Event(name = event_db.DefaultEventName(),
                       case_label = "A",
                       short_name = "sandy")
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


class AuthenticationHandler(base.RequestHandler):
  def get(self):
    org, event = key.CheckAuthorization(self.request)
    if org and event:
      self.redirect(self.request.get('destination', default_value='/'))
      return

    self.response.out.write(template.render({
      "form" : GetOrganizationForm(self.request.POST),
      "destination" : self.request.get('destination', default_value='/'),
      "page" : "/authentication",
    }))

  def post(self):
    now = datetime.datetime.now()
    form = GetOrganizationForm(self.request.POST)
    if not form.validate():
      self.redirect('/authentication')
    event = None
    for e in event_db.Event.gql(
    "WHERE name = :name LIMIT 1", name = form.event.data):
        event = e
    org = None
    for l in organization.Organization.gql(
        "WHERE name = :name LIMIT 1", name = self.request.get("name")):
    # when all orgs have incidents
    #for l in organization.Organization.gql(
            #"WHERE name = :name and incident = :event_key LIMIT 1", name = form.name.data, event_key = event.key()):
      org = l

    if event and org and org.password == form.password.data:
      keys = key.Key.all()
      keys.order("date")
      selected_key = None
      for k in keys:
        age = now - k.date
        # Only use keys created in about the last day,
        # and garbage collect keys older than 2 days.
        if age.days > 14:
          k.delete()
        elif age.days <= 1:
          selected_key = k
      if not selected_key:
        selected_key = key.Key(
            secret_key = ''.join(random.choice(
                string.ascii_uppercase + string.digits)
                                  for x in range(20)))
        selected_key.put()
      self.response.headers.add_header("Set-Cookie",
                                       selected_key.getCookie(org, event))
      self.redirect(urllib.unquote(self.request.get('destination', default_value='/').encode('ascii')))
    else:
      self.redirect(self.request.url)
