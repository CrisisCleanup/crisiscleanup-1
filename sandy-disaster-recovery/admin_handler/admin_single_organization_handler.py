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

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_single_organization.html')


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)
            
        if self.request.get("organization"):
            try:
                id = int(self.request.get("organization"))
            except:
                self.abort(404)
            
            org_by_id = organization.Organization.get_by_id(id)
            org_key = org_by_id.key()
            if not org.may_administer(org_by_id):
                self.abort(403)

            contact_query = db.GqlQuery(
                "SELECT * From Contact WHERE organization = :org_key",
                org_key=org_key
            )

            self.response.out.write(template.render({
                "organization": org_by_id,
                "contacts": contact_query,
                "global_admin": org.is_global_admin,
            }))
            return
        else:
            self.redirect("/admin")