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

from google.appengine.ext import db

# Local libraries.
import base
import organization


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_new_organization.html')


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        # get the new org
        try:
            id = int(self.request.get("new_organization"))
            new_org = organization.Organization.get(db.Key.from_path('Organization', id))
        except:
            self.abort(400)

        # check authorisation
        if not org.may_administer(new_org):
            self.abort(403)

        # lookup contacts
        contacts = db.GqlQuery("SELECT * FROM Contact WHERE organization = :1", new_org.key())

        # render template
        self.response.out.write(template.render({
            "form": True,
            "new_organization": new_org,
            "contacts": contacts,
            "global_admin": org.is_global_admin,
        }))
