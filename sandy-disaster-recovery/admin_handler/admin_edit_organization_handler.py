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
from google.appengine.ext.db import Key

# Local libraries.
import base
import organization
from organization import OrganizationForm, GlobalAdminOrganizationForm


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_edit_org.html')


class AdminHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        try:
            org_by_id = organization.Organization.get_by_id(
                int(self.request.get("organization"))
            )
        except:
            self.abort(404)
            
        # bail if not allowed
        if not org.may_administer(org_by_id):
            self.abort(403)

        form = (
            GlobalAdminOrganizationForm(None, org_by_id) if org.is_global_admin
            else OrganizationForm(None, org_by_id)
        )
        self.response.out.write(template.render({
            "organization": org_by_id,
            "form": form,
        }))

    def AuthenticatedPost(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        try:
            org_by_id = organization.Organization.get_by_id(
                int(self.request.get("organization"))
            )
        except:
            self.abort(404)

        incidents = [
            # hack to workaround apparent bug in webapp2 re multiple selects
            Key(v) for k,v in self.request.POST.items()
            if k.startswith('incidents')
        ]
        form = (
            GlobalAdminOrganizationForm(self.request.POST, incidents=incidents)
            if org.is_global_admin
            else OrganizationForm(self.request.POST, incidents=incidents)
        )

        if form.validate() and not form.errors:
            # bail if not allowed
            if not org.may_administer(org_by_id):
                self.abort(403)

            # update org
            form.populate_obj(org_by_id)
            org_by_id.save()
            self.redirect('/admin-edit-organization?organization=%d' % org_by_id.key().id())
        else:
            self.response.out.write(template.render({
                "organization": org_by_id,
                "form": form,
            }))
