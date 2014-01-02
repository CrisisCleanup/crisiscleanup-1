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
import event_db
import json
import organization
jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class OrganizationAjaxHandler(base.RequestHandler):

    def get(self):
        event_name = self.request.get("event_name")
        event = event_db.Event.all().filter('name', event_name).get()
        if not event:
            self.abort(404)

        event_org_names = [org.name for org in event.organizations]

        other_org_names = [
            org.name for org in organization.Organization.gql(
                'WHERE is_active = True ORDER BY name'
            )
            if org.name not in event_org_names
            and not org.is_admin and not org.deprecated
        ]

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            json.dumps({
                'event_orgs': 
                    ['Admin'] + sorted(
                        name for name in event_org_names if name != 'Admin'
                ),
                'other_orgs': sorted(other_org_names),
            })
        )
