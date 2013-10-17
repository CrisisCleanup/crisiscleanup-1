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

jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_all_organizations.html')
GLOBAL_ADMIN_NAME = "Admin"


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        global_admin = False
        local_admin = False
        
        if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
        if org.is_admin and global_admin == False:
            local_admin = True
            
        if global_admin == False and local_admin == False:
            self.redirect("/")
            return
            
        # get relevant organizations
        if global_admin:
            query = organization.Organization.all()
            
        if local_admin:
            query = organization.Organization.all().filter('incident =', org.incident.key())

        # filter on active/inactive
        if self.request.get('filter') == 'active':
            query.filter('is_active', True)
        elif self.request.get('filter') == 'inactive':
            query.filter('is_active', False)

        self.response.out.write(template.render(
        {
            "global_admin": global_admin,
            "org_query": query,
            "url": "/admin-single-organization?organization=",
        }))
        return
