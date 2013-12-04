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
from google.appengine.ext import db

# Local libraries.
import organization
from admin_base import AdminAuthenticatedHandler
import primary_contact_db


class AdminHandler(AdminAuthenticatedHandler):

    template = "admin_create_contact.html"

    def AuthenticatedGet(self, org, event):
        selected_org_id = self.request.get('selected_org')
        selected_org = (
            organization.Organization.get_by_id(int(selected_org_id))
            if selected_org_id else None
        )

        form = primary_contact_db.ContactFormFull()

        if org.is_global_admin:
            query_string = "SELECT * FROM Organization WHERE org_verified = True"
            organization_list = db.GqlQuery(query_string)
        elif org.is_local_admin:
            organization_list = []
            query_string = "SELECT * FROM Organization WHERE org_verified = True"
            query_first = db.GqlQuery(query_string)
            for q in query_first:
                if q.incident.key() == org.incident.key():
                    organization_list.append(q)
        else:
            raise Exception("Not an administrator")

        self.render(
            form=form,
            organization_list=organization_list,
            selected_org=selected_org,
            create_contact=True,
            global_admin=org.is_global_admin,
            message=self.request.get('message'),
        )
