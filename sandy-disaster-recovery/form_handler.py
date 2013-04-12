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
import cgi
import jinja2
import logging
import os
import urllib2
import wtforms.validators
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
import json



# Local libraries.
import base
import event_db
import site_db
import site_util
import form_db
import site_db



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
logout_template = jinja_environment.get_template('logout.html')
HATTIESBURG_SHORT_NAME = "hattiesburg"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"

class FormHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    #single_site_template = jinja_environment.get_template('single_site.html')
      
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
      
    #if not event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME, "sandy"]:
      #single_site_template = jinja_environment.get_template('single_site_incident_form.html')

      
    message = cgi.escape(self.request.get("message"))
    if len(message) == 0:
      message = None
    form = None
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #form = site_db.DerechosSiteForm()
    #else:
      #form = site_db.SiteForm()
      
    # get event.key()
    # search for form with that event
    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()

    # set it as form_stub
    # send to single site

    inc_form = None
    if query:
      inc_form = query.form_html
    single_site = single_site_template.render(
        { "form": form,
          "org": org,
          "incident_form_block": inc_form,})
    self.response.out.write(template.render(
        {"version" : os.environ['CURRENT_VERSION_ID'],
         "message" : message,
         "logout" : logout_template.render({"org": org, "event": event, "admin": org.is_admin}),
         "single_site" : single_site,
         "form": form,
         "id": None,
         "page": "/",
         "event_name": event.name}))

  def AuthenticatedPost(self, org, event):
    post_data = self.request.POST

    my_string = ""
    for k, v in self.request.POST.iteritems():
      if v == "":
        v = "stub"
      my_string += k + " = '" + v + "', "
    
    
    data = site_db.StandardSiteForm(self.request.POST)
    post_dict = dict(self.request.POST)
    post_json = json.dumps(post_dict)
    
    #single_site_template = jinja_environment.get_template('single_site.html')
      
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
      
    claim_for_org = self.request.get("claim_for_org") == "y"
    #data = None
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
        #data = site_db.DerechosSiteForm(self.request.POST)
    #else:
        #data = site_db.SiteForm(self.request.POST)
        

    # un-escaping data caused by base.py = self.request.POST[i] = cgi.escape(self.request.POST[i])
    data.name.data = site_util.unescape(data.name.data)
    data.priority.data = int(data.priority.data)

    data.name.validators = data.name.validators + [wtforms.validators.Length(min = 1, max = 100,
                             message = "Name must be between 1 and 100 characters")]
    data.phone1.validators = data.phone1.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a primary phone number")]
    data.city.validators = data.city.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a city name")]
    data.state.validators = data.state.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a state name")]
    data.work_type.validators = data.work_type.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please set a primary work type")]
    if data.validate():
      lookup = site_db.Site.gql(
        "WHERE name = :name and address = :address LIMIT 1",
        name = data.name.data,
        address = data.address.data)
      site = None
      for l in lookup:
        # See if this same site is for a different event.
        # If so, we'll make a new one.
        if l.event and l.event.name == event.name:
          site = l
          break

      if not site:
        # Save the data, and redirect to the view page
        site = site_db.Site(address = data.address.data,
                            name = data.name.data,
                            priority = int(data.priority.data))
      for k, v in self.request.POST.iteritems():
	if k not in site_db.STANDARD_SITE_PROPERTIES_LIST:
	  setattr(site, k, v)
      data.populate_obj(site)

      site.reported_by = org
      if claim_for_org:
        site.claimed_by = org
        
      # clear assigned_to if status is unassigned
      if data.status.data == 'Open, unassigned':
        site.assigned_to = ''
      # attempt to save site
      similar_site = None
      if site.similar(event) and not self.request.get('ignore_similar', None):
        similar_site = site.similar(event)
        message = None
      elif site.event or event_db.AddSiteToEvent(site, event.key().id()):
        site_db.PutAndCache(site)
        self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
        return
      else:
        message = "Failed to add site to event: " + event.name
    else:
      message = "Failed to validate"
      similar_site = None
    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()

    # set it as form_stub
    # send to single site

    inc_form = None
    if query:
      inc_form = query.form_html
      
    single_site = single_site_template.render(
        { "form": data,
          "org": org,
          "incident_form_block": inc_form,
          })
    self.response.out.write(template.render(
        {"message": message,
         "similar_site": similar_site,
         "version" : os.environ['CURRENT_VERSION_ID'],
         "errors": data.errors,
         "logout" : logout_template.render({"org": org, "event": event}),
         "single_site": single_site,
         "form": data,
         "id": None,
         "page": "/",
         "post_json": post_json	,
         "event_name": event.name}))
