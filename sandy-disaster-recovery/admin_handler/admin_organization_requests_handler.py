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

from google.appengine.ext import db


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_organization_requests.html')


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        # select orgs to show
        if org.is_global_admin:
            query_string = "SELECT * FROM Organization WHERE org_verified = False"
            query = db.GqlQuery(query_string)
        elif org.is_local_admin:
            query = db.GqlQuery(
                "SELECT * FROM Organization WHERE org_verified = False "
                "AND incidents in :incidents",
                incidents=[incident.key() for incident in org.incidents]
            )

        self.response.out.write(template.render({
            "global_admin": org.is_global_admin,
            "orgs": query,
            "url": "/admin-new-organization?new_organization=",
        }))
