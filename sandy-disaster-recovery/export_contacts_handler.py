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
import primary_contact_db
from google.appengine.ext import db

class ExportContactsHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    self.AuthenticatedPost(org, event)

  def AuthenticatedPost(self, org, event):
    organization = self.request.get("organization")
    org_key = None
    org_query_string = "SELECT * FROM Organization WHERE name = :1"
    org_query = db.GqlQuery(org_query_string, organization)
    
    for r in org_query:
        org_key = r.key()
    query = None
    if organization:
        query_string = "SELECT * FROM Contact WHERE organization = :1"
        query = db.GqlQuery(query_string, org_key)
    else:
        query_string = "SELECT * FROM Contact"
        query = db.GqlQuery(query_string)
        

    filename = 'crisis_cleanup_contacts.csv'
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = (
        'attachment; filename="crisis_cleanup_contacts.csv"')

    writer = csv.writer(self.response.out)
    #Write contacts csv fields
    writer.writerow(primary_contact_db.Contact.CSV_FIELDS)
    for contact in query:
        writer.writerow(contact.ToCsvLine())
    #for contact in query:
      ## come up with this
      #writer.writerow(site.ToCsvLine())
