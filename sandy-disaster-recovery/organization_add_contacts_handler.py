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

from google.appengine.ext import db
import organization
import primary_contact_db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('organization_add_contacts.html')
ten_minutes = 600


class OrganizationAddContactsHandler(base.AuthenticatedHandler):
    
    def _get_org_list(self, org):
        query_string = "SELECT * FROM Organization WHERE name = :1"
        organization_list = db.GqlQuery(query_string, org.name)
        return organization_list

    def AuthenticatedGet(self, authenticated_org, event):
        form = primary_contact_db.ContactFormFull()

        self.response.out.write(template.render({
            "form": form,
            "organization_list": self._get_org_list(authenticated_org),
            "create_contact": True,
        }))
        return
        
    def AuthenticatedPost(self, authenticated_org, event):
        form = primary_contact_db.ContactFormFull(self.request.POST)
        org_id = self.request.get("choose_organization")  # TODO: is this intended?
        try:
            id = int(org_id)
            org = organization.Organization.get_by_id(id)
        except:
            return

        # validate form and save if successful
        if form.validate():
            contact = primary_contact_db.Contact(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                title=form.title.data,
                phone=form.phone.data,
                email=form.email.data,
                is_primary = bool(form.is_primary.data),
                organization = org.key(),
            )
            primary_contact_db.PutAndCache(contact, ten_minutes)
            self.redirect("/organization-settings?message=Contact created. It may take a few moments for the contact to show up on your list.")
            return
        else:
            self.response.out.write(template.render({
                "form": form,
                "organization_list": self._get_org_list(org),
            }))
            return
