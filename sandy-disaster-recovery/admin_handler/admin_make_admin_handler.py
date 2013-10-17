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
import jinja2
import os

# Local libraries.
import base
import cache


import organization
import primary_contact_db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_incident_add_admin.html')
GLOBAL_ADMIN_NAME = "Admin"
ten_minutes = 600


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        global_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
            
        if global_admin == False:
            self.redirect("/")
            return
            
        org_id = self.request.get("organization")
        contact_id = self.request.get("contact")
        
        int_org_id = int(org_id)
        int_contact_id = int(contact_id)
        
        this_organization = organization.Organization.get_by_id(int_org_id)
        this_contact = primary_contact_db.Contact.get_by_id(int_contact_id)

        this_organization.is_admin = True
        cache.PutAndCache(this_organization, 600)
        
        self.redirect("/admin?message=Admin Added")
