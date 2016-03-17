#!/usr/bin/env python
#
# Copyright 2016 Andy Gimma
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

import json
import datetime

import audit_db
import base
dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None


class AdminEmailsHandler(base.RequestHandler):
    def get(self):
        q = audit_db.Audit.all()
        q.filter("action =", "login")
        audits = q.fetch(2500)
        contacts = {}

        contacts = {}
        for audit in audits:
        	if audit.email == "" or audit.email == "null" or audit.email == None:
        		pass
        	else:
	        	if audit.email.lower() in contacts:
	        		pass
	        	else:
	        		contacts[audit.email.lower()] = []

	        	uniq_orgs = contacts[audit.email.lower()]
	        	if str(audit.initiated_by.key()) not in uniq_orgs:
	        		if audit.email.lower() == "missourifloodresponse@gmail.com" and str(audit.initiated_by.key()) == "ahlzfnNhbmR5LWRpc2FzdGVyLXJlY292ZXJ5chkLEgxPcmdhbml6YXRpb24YgICAyOWViAkM":
	        			pass
	        		elif "aaron.l" in audit.email.lower() and str(audit.initiated_by.key()) == "ahlzfnNhbmR5LWRpc2FzdGVyLXJlY292ZXJ5chkLEgxPcmdhbml6YXRpb24YgICAuJPNhQkM":
	        			pass
	        		else:
		        		contacts[audit.email.lower()].append(str(audit.initiated_by.key()))
    	self.response.write(json.dumps(contacts))





