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

class SitesHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    county = self.request.get("county", default_value = "NoCounty")
    if county == "NoCounty":
      query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    else:
      logging.critical(county)
      query = db.GqlQuery("SELECT * FROM Site WHERE county = :county "
                          "ORDER BY name",
                          county = county)
    for s in query:
      self.response.out.write(
          '<a href="/edit?id=%(id)s">Edit</a> '
          '<a href="/delete?id=%(id)s">Delete</a> - ' % {'id' : s.key().id() })
      self.response.out.write("%s: %s - %s<br />" %
                              (s.case_number, s.name, s.address))
