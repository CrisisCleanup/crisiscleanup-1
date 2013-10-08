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
import organization

from google.appengine.ext import db

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('organization_settings.html')


class OrganizationSettingsHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, authenticated_org, event):
        # decide what org to lookup
        org = organization.Organization.get_by_id(authenticated_org.key().id())  # hardcoded
        if org.is_admin:
            contacts = db.GqlQuery("SELECT * From IncidentAdmin WHERE incident = :1", org.incident.key())
        else:
            contacts = db.GqlQuery("SELECT * From Contact WHERE organization = :org_key", org_key = org.key())
        self.response.out.write(template.render({
            "organization": org,
            "contacts": contacts,
            "message": self.request.get("message"),
            "is_admin": org.is_admin,
        }))
