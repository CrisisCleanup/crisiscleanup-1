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

from primary_contact_db import Contact, ContactFormFull

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_edit_contact.html')
GLOBAL_ADMIN_NAME = "Admin"


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, _):
        global_admin = False
        local_admin = False
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
        
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return
            
        if self.request.get("contact"):
            # lookup contact
            try:
                id = int(self.request.get("contact"))
            except:
                pass
            contact = Contact.get_by_id(id)

            # bail if not a relevant local admin
            if local_admin:
                if not org.incident.key() == contact.organization.incident.key():
                    self.redirect("/")
                    return
            
            # create form
            form = ContactFormFull(None, contact)

            # render template
            self.response.out.write(template.render({
                "contact": contact,
                "form": form,
                "organization_name": (
                    contact.organization.name if contact.organization else None
                ),
                "global_admin": global_admin,
            }))

    def AuthenticatedPost(self, org, _):
        global_admin = False
        local_admin = False
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin == True and global_admin == False:
            local_admin = True
        
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return

        form = ContactFormFull(self.request.POST)
        if form.validate() and not form.errors:
            # update contact
            contact_id = int(self.request.get("contact_id"))
            contact = Contact.get_by_id(contact_id)

            # bail if not a relevant local admin
            if local_admin:
                if not org.incident.key() == contact.organization.incident.key():
                    self.redirect("/")
                    return

            form.populate_obj(contact)
            contact.save()
            self.redirect('/admin-single-contact?contact=%d' % contact.key().id())
        else:
            self.response.out.write(template.render({
                "contact": contact,
                "form": form,
                "organization_name": (
                    contact.organization.name if contact.organization else None
                ),
                "global_admin": global_admin,
            }))
