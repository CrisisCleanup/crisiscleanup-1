#!/usr/bin/env python
#
# Copyright 2013 Chris Wood
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# System libraries.
import StringIO
import csv
import json
import logging

from google.appengine.ext.db import Query, BadValueError
from google.appengine.api.urlfetch import fetch

# Local libraries.
import base
import event_db
import site_db
from organization import Organization
from primary_contact_db import Contact

# constants
GLOBAL_ADMIN_NAME = "Admin"

def check_and_write_row(row_d):
    """
    Check and save @row_d, return True if ok and False if failed.
    """
    row_acceptable = bool(row_d['Date Password Provided'])
    if row_acceptable:
        # get org
        query = Query(model_class=Organization)
        query.filter('name = ', row_d['ORGANIZATION'])
        org = query.get()
        if org:
            try:
                # write new contact
                new_contact = Contact(
                    first_name=row_d['First Name'],
                    last_name=row_d['Last Name'],
                    email=row_d['E-MAIL'],
                    phone=row_d['PHONE #'],
                    organization=org,
                )
                new_contact.save()
                return True
            except BadValueError, e:
                pass
    return False


class ImportContactsHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        # check auth
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
                global_admin = True
        if org.is_admin == True and global_admin == False:
                local_admin = True
                
        if global_admin == False and local_admin == False:
                self.redirect("/")
                return

        # return form
        h = """<html><body>
                <h1>Import Contacts</h1>
                <p><b>Warning:</b> this will immediately write to the datastore.</p>
                <form enctype="multipart/form-data" method="post">
                <label>File: <input name='file' type="file"></label>
                <br>
                <input type="submit" value="Upload">
                </form>
                </body></html>"""
        self.response.out.write(h)

    def AuthenticatedPost(self, org, event):
        # check auth
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
                global_admin = True
        if org.is_admin == True and global_admin == False:
                local_admin = True
                
        if global_admin == False and local_admin == False:
                self.redirect("/")
                return

        # read from csv and write
        csv_file = self.request.params['file'].file
        csv_dict_reader = csv.DictReader(csv_file)
        headings = csv_dict_reader.fieldnames
        accepted_rows = []
        skipped_rows = []
        for row in csv_dict_reader:
            success = check_and_write_row(row)
            if success:
                accepted_rows.append(row)
            else:
                skipped_rows.append(row)

        # construct output
        output = "Problems:\n\n"
        output += ','.join(headings) + '\n'
        s = StringIO.StringIO()
        dict_writer = csv.DictWriter(s, headings)
        for row in skipped_rows:
            dict_writer.writerow(row)
        s.seek(0)
        output += s.read()
        output += "\n\nAccepted:\n\n"
        output += ','.join(headings) + '\n'
        s = StringIO.StringIO()
        dict_writer = csv.DictWriter(s, headings)
        for row in accepted_rows:
            dict_writer.writerow(row)
        s.seek(0)
        output += s.read()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(output)

