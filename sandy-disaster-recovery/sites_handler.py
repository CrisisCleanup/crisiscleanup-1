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
import os
from google.appengine.ext import db

# Local libraries.
import base
import cgi
import jinja2


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('sites.html')

SITES_PER_PAGE = 200


class SitesHandler(base.AuthenticatedHandler):

  def AuthenticatedGet(self, org, event):
    try:
        page = max(0, int(self.request.get("page", 0)))
    except ValueError:
        page = 0
    message = cgi.escape(self.request.get("message"))
    order = cgi.escape(self.request.get("order", "name"))
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
      query_string = "SELECT * FROM Site WHERE event = :event_key" + order_string +" LIMIT %s OFFSET %s" % (SITES_PER_PAGE, page * SITES_PER_PAGE)      
      
      query = db.GqlQuery(query_string, event_key = event.key())
        
    else:
      query_string = "SELECT * FROM Site WHERE county = :county and event = :event_key " + order_string + " LIMIT %s OFFSET %s" % (SITES_PER_PAGE, page * SITES_PER_PAGE)
      query = db.GqlQuery(query_string, where_variable = county, event_key = event.key())
      
    self.response.out.write(template.render(
    {
	"sites_query": query,
	"page_number": page,
        "sites_per_page": SITES_PER_PAGE,
    }))
