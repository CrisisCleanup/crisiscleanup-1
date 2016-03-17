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
import audit_db
import base

class AdminEmailsHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        q = audit_db.Audit.all()
        q.filter("action =", "login")
        audits = q.fetch(2500)
        contacts = {}

        contacts = {}
        for audit in audits:
        	if audit.email in contacts:
        		pass
        	else:
        		contacts[audit.email] = []

        	
        	contacts[audit.email].append(audit.initiated_by.key())
        	contacts[audit.email] = set(contacts[audit.email])
    	self.response.write(contacts)




