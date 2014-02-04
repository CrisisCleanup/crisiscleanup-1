#!/usr/bin/env python
#
# Copyright 2012 Andrew Gimma
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
import csv

# Local libraries.
import base
from primary_contact_db import Contact


class ExportContactsHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        return self.handle(org, event)

    def AuthenticatedPost(self, org, event):
        return self.handle(org, event)

    def handle(self, org, event):
        org_id = self.request.get("org")

        # select contacts
        relevant_contacts = Contact.for_event(event)
        if org_id:
            relevant_contacts = (
                contact for contact in relevant_contacts
                if unicode(contact.organization.key().id()) == org_id
            )

        # write out csv
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.headers['Content-Disposition'] = \
            'attachment; filename="crisis_cleanup_contacts.csv"'
        writer = csv.writer(self.response.out)
        writer.writerow(Contact.CSV_FIELDS)
        for contact in relevant_contacts:
            writer.writerow(contact.ToCsvLine())
