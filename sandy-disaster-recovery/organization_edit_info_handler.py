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
template = jinja_environment.get_template('organization_edit_info.html')


class OrganizationEditInfoHandler(base.AuthenticatedHandler):

    def AuthenticatedPost(self, org, event):
        """ Update info details of authenticated org. """
        form = organization.OrganizationInformationForm(self.request.POST)
        if form.validate():
            form.populate_obj(org)
            import logging; logging.error('HERE!!!!!')
            org.save()
            organization.PutAndCache(org, 600)
            self.redirect("/organization-settings")
            return
        else:
            self.response.out.write(template.render({
                "form": form,
                "org": org
            }))
            return

    def AuthenticatedGet(self, authenticated_org, event):
        """
        Show the edit form of the authenticated organization.
        """
        # decide what org to lookup
        org = organization.Organization.get_by_id(authenticated_org.key().id())  # hardcoded

        form = organization.OrganizationInformationForm(None, org)

        self.response.out.write(template.render({
            "form": form,
            "org": org
        }))
