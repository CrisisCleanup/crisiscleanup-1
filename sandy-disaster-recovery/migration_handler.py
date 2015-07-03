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

	    # if self.request.get("action") == "get_entity_by_key":
	    # 	table = json_request["table"]
	    # 	key = json_request["key"]
	    # 	if table == "site":
	    # 		site = site_db.Site.all()
	    # 		site.filter('event', json_request["event_key"])
	    # 		site.filter('key', json_request["object_key"])
	    # 		self.response.out.write(json.dumps(site.get(), default = dthandler))

	    # 	if table == "event":
	    # 		event = event_db.Event.all()
	    # 		event.filter('key', json_request["object_key"])
	    # 		self.response.out.write(json.dumps(event.get(), default = dthandler))	    		

	    # 	if table == "org":
	    # 		organization = organization.Organization.all()
	    # 		organization.filter('key', json_request["object_key"])
	    # 		self.response.out.write(json.dumps(organization.get(), default = dthandler))

	    # 	if table == "contact":
	    # 		contact = primary_contact_db.Contact.all()
	    # 		contact.filter('key', json_request["object_key"])
	    # 		self.response.out.write(json.dumps(contact.get(), default = dthandler))	    		