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

# Local libraries.
import base

from primary_contact_db import Contact


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('see_all_contacts.html')


class SeeAllContactsHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        all_contacts_query = Contact.all()
        relevant_contacts = (
            contact for contact in all_contacts_query
            if contact.organization
            and contact.organization.may_access(event)
        )

        self.response.out.write(template.render(
        {
            "contacts": relevant_contacts,
        }))
