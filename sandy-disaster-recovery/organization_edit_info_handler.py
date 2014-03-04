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

import base
import organization


class OrganizationEditInfoHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'organization_edit_info.html'

    def AuthenticatedPost(self, org, event):
        """ Update info details of authenticated org. """
        form = organization.OrganizationInformationForm(self.request.POST)
        if form.validate():
            form.populate_obj(org)
            org.save()
            organization.PutAndCache(org, 600)
            return self.redirect("/organization-settings")
        else:
            return self.render(
                form=form,
                org=org
            )

    def AuthenticatedGet(self, authenticated_org, event):
        """
        Show the edit form of the authenticated organization.
        """
        # decide what org to lookup
        org = organization.Organization.get_by_id(authenticated_org.key().id())  # hardcoded

        form = organization.OrganizationInformationForm(None, org)

        return self.render(
            form=form,
            org=org
        )
