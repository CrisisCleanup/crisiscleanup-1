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
import json
import logging
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db
import cgi
import key

class SitesHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    message = cgi.escape(self.request.get("message"))
    order = cgi.escape(self.request.get("order", "name"))
    if message:
      self.response.out.write(message + "<br /><br />")
      
    self.response.out.write("<a href='/sites?order=request_date'>Order by date created</a><br />")
    self.response.out.write("<a href='/sites?order=name'>Order by name</a><br /><br/>")
    
    
    county = self.request.get("county", default_value = "NoCounty")
    
    # GQL query string builder
    # escapes WHERE clause with :where_variable
    # system is throwing errors when I try to escape ORDER BY
    # so instead I'm curating with an if/else statement
    # GQL can't do anything destructive (like delete an entity)
    # but I still feel more comfortable with protecting this against future changes to GQL
    
    select_string = "SELECT * FROM Site "
    where_string = "WHERE county = :where_variable" # and event = :event_key"
    where_event = "WHERE event = :event_key "

    if order == "name":  
      order_string = "ORDER BY name"
    elif order == "request_date":
      order_string = "ORDER BY request_date"
    # end query string
    
    if county == "NoCounty":
      query_string = select_string + order_string
      query = db.GqlQuery(query_string, event_key = event.key())
        
    else:
      logging.critical(county)
      query_string = select_string + where_string + order_string + order
      query = db.GqlQuery(query_string, where_variable = county, event_key = event.key())
      
    for s in query:
      self.response.out.write(
          '<a href="/edit?id=%(id)s">Edit</a> '
          '<a href="/delete?id=%(id)s">Delete</a> - ' % {'id' : s.key().id() })
      self.response.out.write("%s: %s - %s<br />" %
                              (s.case_number, s.name, s.address))
