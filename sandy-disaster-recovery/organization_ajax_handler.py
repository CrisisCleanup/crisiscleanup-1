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
import json

# Local libraries.
import base
from event_db import Event
from organization import Organization


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class OrganizationAjaxHandler(base.RequestHandler):

    def get(self):
        # select event
        event_name = self.request.get("event_name")
        event = Event.all().filter('name', event_name).get()
        if not event:
            self.abort(404)

        # get names of active orgs in and out of the event
        event_org_names = sorted(
            Organization.names_by_search(event=event, is_active=True)
        )

        other_org_names = sorted(
            filter(
                lambda name: name not in event_org_names,
                Organization.names_by_search(
                    is_active=True,
                    is_admin=False,
                    deprecated=False
                )
            )
        )

        # return json
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
