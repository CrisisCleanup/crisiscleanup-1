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
from collections import OrderedDict
# Local libraries.
import base
import key
import site_db
import event_db

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]

class PublicMapAjaxHandler(base.RequestHandler):      
  def get(self):
    logging.debug("PublicMapAjaxHandler")
    event_shortname = self.request.get("shortname")
    page = self.request.get("page")
    page_int = int(page)

    event = None
    events = event_db.GetAllCached()
    for e in events:
      if e.short_name == event_shortname:
	event = e
    #logging.debug(event.name)
    #q = Query(model_class = site_db.Site)#, projection=('latitude', 'longitude','id', 'status', 'claimed_by', 'work_type', 'derechos_work_type', 'case_number', 'floors_affected'))


    ids = []
  #filter by event
    #status = "open"
    #q.filter("event =", event.key())
    #q.is_keys_only()
    #if status == "open":
	#logging.debug("status == open")
	#q.filter("status >= ", "Open")
    #elif status == "closed":
	#q.filter("status < ", "Open")
	#logging.debug("status == closed")
    #logging.debug("status = " + status)
	
    #query = q.fetch(PAGE_OFFSET, offset = page_int * PAGE_OFFSET)
    #for q in query:
	#ids.append(q.key().id())
    #q = db.Query(site_db.Site, projection=('latitude', 'longitude','id', 'status', 'claimed_by', 'work_type', 'derechos_work_type', 'case_number', 'floors_affected'), filter('status >=', "open"))
    #q = site_db.Site.gql("SELECT latitude, longitude, id, claimed_by, work_type, derechos_work_type, case_number, floors_affected WHERE status >= open")
    where_string = "Open"
    gql_string = 'SELECT latitude, longitude, claimed_by, work_type, case_number, floors_affected FROM Site WHERE status >= :1 and event = :2'# WHERE status >= %s", where_string
    q = db.GqlQuery(gql_string, where_string, event.key())


    this_offset = page_int * PAGE_OFFSET
    logging.debug("this_offset = " + str(this_offset))
	
    ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]
    logging.debug("ids len = " + str(len(ids)))
	
    output = json.dumps(
	[s[1] for s in site_db.GetAllCached(event, ids)],
	default=dthandler)
    self.response.out.write(output)
    return
        
    #self.response.out.write(output)

    
