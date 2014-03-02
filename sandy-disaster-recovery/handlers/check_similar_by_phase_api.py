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
import metaphone
from models import phase

PAGE_OFFSET = 100


dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class CheckSimilarByPhaseAPI(base.AuthenticatedHandler):      
  def AuthenticatedGet(self, org, event):
    phase_id = self.request.get('phase_id')
    address = self.request.get("address")
    name = self.request.get("name")
    zip_code = self.request.get("zip_code")
    
    #if not phase_id and address and name:
      #return
    
    
    #create metaphones
    
    name_metaphone = '%s-%s' % metaphone.dm(unicode(name)) if name else None
    address_metaphone = '%s-%s' % metaphone.dm(unicode(address)) if address else None
    
        
    q = Query(model_class = site_db.Site)
    q.filter("event =", event.key())
    q.filter("name_metaphone =", name_metaphone)
    q.filter("address_metaphone =", address_metaphone)
    
    site = q.get()
    
    #raise Exception(site.phase_id)
    if not site:
      return
    
    q = Query(model_class = phase.Phase)
    q.filter("phase_id =", phase_id)
    q.filter("site =", site.key())
    
    phase_obj = q.get()
    if phase_obj:
      self.response.out.write(
        json.dumps(phase.PhaseToDict(phase_obj), default = dthandler))
      return
    self.response.out.write(
        json.dumps(site_db.SiteToDict(site), default = dthandler))
