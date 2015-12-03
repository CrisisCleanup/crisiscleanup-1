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

PAGE_OFFSET = 100


dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class SiteAjaxHandler(base.AuthenticatedHandler):      
  def AuthenticatedGet(self, org, event):
    id_param = self.request.get('id')
    latitude_param = self.request.get("latitude")
    longitude_param = self.request.get("longitude")
    
    if latitude_param and longitude_param:
      try:
        latitude = float(latitude_param)
        longitude = float(longitude_param)
      except:
        self.response.set_status(404)
      json_array = []
      for site in site_db.Site.gql(
           'Where latitude = :1 and longitude = :2 and event = :3', latitude, longitude, event.key()):
        json_string = json.dumps({
            "id": site.key().id(),
            "address": site.address,
        })
        json_array.append(json_string)
      self.response.out.write(
            json.dumps(json_array, default = dthandler))      
      return
      
    if id_param == "all":
        status = self.request.get("status", default_value = "")
        page = self.request.get("page", default_value = "0")
        page_int = int(page)
        logging.debug("page = " + page)
        
        #query_string = "SELECT * FROM Site WHERE event = :event_key LIMIT %s OFFSET %s" % (PAGE_OFFSET, page_int * PAGE_OFFSET)   
        ##logging.debug("OFFSET = " + PAGE_OFFSET)
        ##logging.debug("page * OFFSET = " + page_int * PAGE_OFFSET)
        
        #query = db.GqlQuery(query_string, event_key = event.key())
        q = Query(model_class = site_db.Site)
       
        ids = []
      #filter by event
        q.filter("event =", event.key())
        q.is_keys_only()
        if status == "open":
            logging.debug("status == open")
            q.filter("status >= ", "Open")
        elif status == "closed":
            q.filter("status < ", "Open")
            logging.debug("status == closed")
        logging.debug("status = " + status)
            
        #query = q.fetch(PAGE_OFFSET, offset = page_int * PAGE_OFFSET)
        #for q in query:
            #ids.append(q.key().id())
            
        this_offset = page_int * PAGE_OFFSET
        logging.debug("this_offset = " + str(this_offset))
            
        ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]
        logging.debug("ids len = " + str(len(ids)))
           
        output = json.dumps(
            [s[1] for s in site_db.GetAllCached(event, ids)],
            default=dthandler)
        self.response.out.write(output)
        return
        
        
    #if id_param == "all":
      #county = self.request.get("county", default_value = "all")
      #status = self.request.get("status", default_value = "")
      #q = Query(model_class = site_db.Site, keys_only = True)
      
      ##filter by event
      #q.filter("event =", event.key())
      #if status == "open":
        #q.filter("status >= ", "Open")
      #elif status == "closed":
        #q.filter("status < ", "Open")
      #if county != "all":
        #q.filter("county =", county)

      #ids = [key.id() for key in q.run(batch_size = 2000)]
      #output = json.dumps(
        #[s[1] for s in site_db.GetAllCached(event, ids)],
        #default=dthandler)
      #self.response.out.write(output)
      #return
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
