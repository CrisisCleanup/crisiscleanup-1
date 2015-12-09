#!/usr/bin/env python
#
# Copyright 2015 Andrew Gimma
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
import logging



from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import Query
from google.appengine.api import search

# Local libraries.
import site_db
import organization
# import metaphone

class Audit(db.Expando):
	created_at = db.DateTimeProperty(auto_now_add=True, required = True)
	action = db.StringProperty(choices=["create", "edit", "login", "generate_new_password"], required = True)
	initiated_by = db.ReferenceProperty(organization.Organization, required = True)
	site = db.ReferenceProperty(site_db.Site)
	ip = db.StringProperty()
	password_hash = db.StringProperty()


def create(site, action, org):
	audit = Audit(action = action, site = site, initiated_by = org)
	site_dict = site_db.SiteToDict(site)
	for attr in site_dict:
		try:
			setattr(audit, attr, getattr(site, attr))
		except:
			if attr != "id":
				setattr(audit, attr, getattr(site, attr).key())
	audit.put()

def login(ip, org, password_hash, org_name, event_name):
	audit = Audit(action = "login", ip = ip, initiated_by = org, password_hash = password_hash, org_name = org_name, event_name = event_name)
	audit.put()

def new_password(org, password_hash):
	audit = Audit(action = "generate_new_password", initiated_by = org, password_hash = password_hash)
	audit.put()


