#!/usr/bin/env python
#
# Copyright 2012 Andy Gimma
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
import os
import jinja2
from google.appengine.ext import db

# Local libraries.
import base


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('see_all_contacts.html')


class SeeAllContactsHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        contacts = None
        order_string = ""
        if self.request.get("order"):
            order_kind = self.request.get("order")
            order_string = " ORDER BY " + order_kind

        query_string = "SELECT * FROM Contact" + order_string

        contacts = db.GqlQuery(query_string)    
        final_list = []
        for q in contacts:
            if q.organization:
                if event.key() in (inc.key() for inc in q.organization.incidents):
                    final_list.append(q)
            
        self.response.out.write(template.render(
        {
            "contacts": final_list,
            "display_contacts": True,
        }))
