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
import random_password

PAGE_OFFSET = 200
class SitesHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    page = cgi.escape(self.request.get("page"))  
    if not page:
        page = "0"
    logging.debug("page = " + page)
    try:
        page = int(page)
    except:
        print "error"
    message = cgi.escape(self.request.get("message"))
    order = cgi.escape(self.request.get("order", "name"))
    if message:
      self.response.out.write(message + "<br /><br />")
      
    self.response.out.write("<a href='/sites?order=request_date'>Order by date created</a><br />")
    self.response.out.write("<a href='/sites?order=name'>Order by name</a><br /><br/>")
    next_page =  page + 1
    page_link = "<a href='/sites?page=%d'>Next Page</a><br /><br/>" % next_page
    self.response.out.write(page_link)
    self.response.out.write("200 shown per page")
    self.response.out.write(message + "<br /><br />")
    
    
    
    
    
    county = self.request.get("county", default_value = "NoCounty")
    
    # GQL query string builder
    # escapes WHERE clause with :where_variable
    # system is throwing errors when I try to escape ORDER BY
    # so instead I'm curating with an if/else statement
    # GQL can't do anything destructive (like delete an entity)
    # but I still feel more comfortable with protecting this against future changes to GQL
    if order == "name":  
      order_string = " ORDER BY name"
    elif order == "request_date":
      order_string = " ORDER BY request_date"
    # end query string
    
    if county == "NoCounty":
      query_string = "SELECT * FROM Site WHERE event = :event_key" + order_string +" LIMIT %s OFFSET %s" % (PAGE_OFFSET, page * PAGE_OFFSET)      
      
      query = db.GqlQuery(query_string, event_key = event.key())
        
    else:
      logging.critical(county)
      query_string = "SELECT * FROM Site WHERE county = :county and event = :event_key " + order_string + " LIMIT %s OFFSET %s" % (PAGE_OFFSET, page * PAGE_OFFSET)
      query = db.GqlQuery(query_string, where_variable = county, event_key = event.key())
      
    for s in query:
      self.response.out.write(
          '<a href="/edit?id=%(id)s">Edit</a> '
          '<a href="/delete?id=%(id)s">Delete</a> - ' % {'id' : s.key().id() })
      self.response.out.write("%s: %s - %s<br />" %
                              (s.case_number, s.name, s.address))
