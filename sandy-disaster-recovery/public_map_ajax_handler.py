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
from google.appengine.ext import db
from google.appengine.ext.db import Query

# Local libraries
import base
import site_db
import event_db

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class PublicMapAjaxHandler(base.RequestHandler):      

  def get(self):
    event_shortname = self.request.get("shortname")
    page = self.request.get("page")
    page_int = int(page)

    if event_shortname == None:
      event_shortname = "sandy"
    event = None
    events = event_db.GetAllCached()
    for e in events:
      if e.name == event_shortname:
	event = e

      
    ids = []
    where_string = "Open"
    q = None
    if event.short_name != 'moore':
      gql_string = 'SELECT * FROM Site WHERE status >= :1 and event = :2'
      q = db.GqlQuery(gql_string, where_string, event.key())

    else:
      q = Query(model_class = site_db.Site)

      q.filter("event =", event.key())
      q.is_keys_only()
      q.filter("status >= ", "Open")
	  
      this_offset = page_int * PAGE_OFFSET
	  
      ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]
           
    this_offset = page_int * PAGE_OFFSET
	
    ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]

    def public_site_filter(site):
        # site as dict
        return {
            'event': site['event'],
            'id': site['id'],
            'case_number': site['case_number'],
            'work_type': site['work_type'],
            'status': site['status'],
            'blurred_latitude': site.get('blurred_latitude'),
            'blurred_longitude': site.get('blurred_longitude'),
        }
	
    output = json.dumps(
	[public_site_filter(s[1]) for s in site_db.GetAllCached(event, ids)],
	default=dthandler
    )
    self.response.out.write(output)
