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
from urlparse import urlparse

# Local libraries.
import base
import event_db
import key
import organization
import primary_contact_db
import site_db
import page_db
from messaging import email_administrators_using_templates
import generate_hash
import audit_db

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
    organization.PutAndCache(admin_org)
    
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


class AuthenticationHandler(base.RequestHandler):

  def get(self):
    org, event = key.CheckAuthorization(self.request)
    if org and event:
      self.redirect(urllib.unquote(self.request.get('destination', default_value='/')).encode('ascii'))
      return

    template_params = page_db.get_page_block_dict()
    template_params.update({
      "form" : GetOrganizationForm(self.request.POST),
      "destination" : self.request.get('destination', default_value='/'),
      "page" : "/authentication",
      "error_message": self.request.get("error_message"),
      "initial_event_name": self.request.get("initial_event_name", ""),
    })
    self.response.out.write(template.render(template_params))

  def post(self):
    # raise Exception(self.request)
    now = datetime.datetime.now()
    form = GetOrganizationForm(self.request.POST)
    if not form.validate():
      self.redirect('/authentication')
    event = None
    for e in event_db.Event.gql(
    "WHERE name = :name LIMIT 1", name = form.event.data):
        event = e

    # check org and incident match
    org = None
    selected_org_name = self.request.get("name")
    if selected_org_name == "Other":
      selected_org_name = self.request.get("existing-organization")
    if selected_org_name == "Admin":
      # admin user
      for x in organization.Organization.gql(
    "WHERE name = :name LIMIT 1", name=selected_org_name
      ):
        org = x
    else:
      # regular user
      for x in organization.Organization.gql(
    "WHERE name = :name AND incidents = :incident LIMIT 1",
          name=selected_org_name,
          incident=event.key()
      ):
        org = x
      if org is None:
          # try legacy incident field
          for x in organization.Organization.gql(
              "WHERE name = :name and incident = :incident LIMIT 1",
              name=selected_org_name,
              incident=event.key()
          ):
              org = x

    # handle verified+active existing org joining new incident
    if not org and selected_org_name == 'Other':
        existing_org_name = self.request.get("existing-organization")
        for x in organization.Organization.gql(
            "WHERE name = :name LIMIT 1", name=existing_org_name):
            org = x

    # hash here, test if event and org and password_hash(form.password.data) in org.password_hash_list
    if event and org and generate_hash.recursive_hash(form.password.data) in org._password_hash_list:
    # if event and org and org.password == form.password.data:
      # login was successful
      audit_db.login(org_name = org.name, ip=self.request.remote_addr, org = org, password_hash = generate_hash.recursive_hash(form.password.data), event = event.name)
      # (temp) force migration of org.incident -> org.incidents
      unicode(org.incidents)

      # add org to incident if not already allowed
      if not org.may_access(event):
          org.join(event)
          logging.info(
            u"authentication_handler: "
            u"Existing organization %s has joined incident %s." % (
                org.name, event.name
            )
          )

          # email administrators
          review_url = "%s://%s/admin-single-organization?organization=%s" % (
              urlparse(self.request.url).scheme,
              urlparse(self.request.url).netloc,
              org.key().id()
          )
          organization_form = organization.OrganizationForm(None, org)
          email_administrators_using_templates(
            event=event,
            subject_template_name='organization_joins_incident.to_admins.subject.txt',
            body_template_name='organization_joins_incident.to_admins.body.txt',
            organization=org,
            review_url=review_url,
            organization_form=organization_form,
          )
          org.save()

      # timestamp login
      now = datetime.datetime.utcnow()
      org.timestamp_login = now
      org.save()
      event.timestamp_last_login = now
      event.save()

      # create login key
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

      # set cookie of org and event
      self.response.headers.add_header("Set-Cookie",
                                       selected_key.getCookie(org, event))
      self.redirect(urllib.unquote(self.request.get('destination', default_value='/').encode('ascii')))
    else:
      self.redirect(self.request.url + "?error_message=Incorrect Organization and Passcode Combination")
