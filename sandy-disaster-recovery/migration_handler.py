import datetime
import jinja2
import cgi
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
import organization
import event_db
import primary_contact_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

class MigrationHandler(base.RequestHandler):
    def get(self):

	    if self.request.get("action") == "event_keys":
	    	keys = []
	    	events = event_db.Event.all(keys_only=True)
	    	for event in events:
	    		keys.append(str(event))
	    	for key in keys:
	    		k = db.Key(key)
	    		raise Exception(k)
	    	self.response.out.write(json.dumps(keys))
	    	return

	    if self.request.get("action") == "org_keys":
	    	keys = []
	    	organizations = organization.Organization.all(keys_only=True)
	    	for org in organizations:
	    		keys.append(str(org))
	    	self.response.out.write(json.dumps(keys))
	    	return

	    if self.request.get("action") == "contact_keys":
	    	keys = []
	    	contacts = primary_contact_db.Contact.all(keys_only=True)
	    	for contact in contacts:
	    		keys.append(str(contact))
	    	self.response.out.write(json.dumps(keys))
	    	return

	    if self.request.get("action") == "site_keys":
	    	keys = []
	    	sites = site_db.Site.all(keys_only=True)
	    	#filter by event
	    	for site in sites:
	    		keys.append(str(site))
	    	self.response.out.write(json.dumps(keys))
	    	return

	    if self.request.get("action") == "get_entity_by_key":
	    	table = self.request.get("table")
	    	key = self.request.get("key")

	    	if table == "event":
	    		events = event_db.Event.all()
	    		events.filter("__key__ =", db.Key(self.request.get("key")))
	    		event = events.get()
	    		event_dict = to_dict(event)
	    		event_dict["id"] = event.key().id()
	    		event_dict["key"] = str(event.key())
	    		self.response.out.write(json.dumps(event_dict, default = dthandler))

	    	if table == "site":
	    		sites = site_db.Site.all()
	    		sites.filter("__key__ =", db.Key(self.request.get("key")))
	    		site = sites.get()
	    		site_dict = to_dict(site)
	    		site_dict["id"] = site.key().id()
	    		site_dict["key"] = str(site.key())
	    		self.response.out.write(json.dumps(site_dict, default = dthandler))

	    	if table == "organization":
	    		organizations = organization.Organization.all()
	    		organizations.filter("__key__ =", db.Key(self.request.get("key")))
	    		organization = organizations.get()
	    		org_dict = to_dict(org)
	    		org_dict["id"] = org.key().id()
	    		org_dict["key"] = str(org.key())
	    		self.response.out.write(json.dumps(org_dict, default = dthandler))

	    	if table == "contact":
	    		contacts = primary_contact_db.Contact.all()
	    		contacts.filter("__key__ =", db.Key(self.request.get("key")))
	    		contact = contacts.get()
	    		contact_dict = to_dict(contact)
	    		contact_dict["id"] = contact.key().id()
	    		contact_dict["key"] = str(contact.key())
	    		self.response.out.write(json.dumps(contact_dict, default = dthandler))
