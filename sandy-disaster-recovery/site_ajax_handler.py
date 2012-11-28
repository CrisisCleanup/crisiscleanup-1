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
import json
import logging
import os
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import Query
# Local libraries.
import base
import key
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class SiteAjaxHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    id_param = self.request.get('id')
    if id_param == "all":
      county = self.request.get("county", default_value = "all")
      status = self.request.get("status", default_value = "")
      q = Query(model_class = site_db.Site, keys_only = True)
      if status == "open":
        q.filter("status >= ", "Open")
      elif status == "closed":
        q.filter("status < ", "Open")
      if county != "all":
        q.filter("county =", county)
      ids = [key.id() for key in q.run(batch_size = 2000)]
      output = json.dumps(
        [s[1] for s in site_db.GetAllCached(event, ids)],
        default=dthandler)
      self.response.out.write(output)
      return
    try:
      id = int(id_param)
    except:
      self.response.set_status(404)
      return
    site = site_db.GetAndCache(id)
    if not site:
      self.response.set_status(404)
      return
    # TODO(jeremy): Add the various fixes for Flash
    # and other vulnerabilities caused by having user-generated
    # content in JSON strings, by setting this as an attachment
    # and prepending the proper garbage strings.
    # Javascript security is really a pain.
    self.response.out.write(
        json.dumps(site_db.SiteToDict(site), default = dthandler))
