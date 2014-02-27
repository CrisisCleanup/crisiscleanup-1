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
from google.appengine.ext import db

# Local libraries.
import base
import organization


class OrganizationInfoHandler(base.FrontEndAuthenticatedHandler):

    template_filenames = ['organization_info.html', 'organizations_display_all.html']

    def AuthenticatedGet(self, org, event):
        id = None
        try:
            id = int(self.request.get("organization", 0))
        except:
	    id = None
        message = self.request.get("message")

        # show all orgs if no id
        if not id:
            query_string = "SELECT * FROM Organization WHERE incidents = :1 ORDER BY name"
            organizations = db.GqlQuery(query_string, event.key())
            return self.render(
                template='organizations_display_all.html',
                org_query=organizations,
                message=message
            )

        # lookup and show the chosen org
        org_by_id = organization.Organization.get_by_id(id)
        if not org_by_id:
            self.redirect("organization-info?message=Organization not found. If you think you are seeing this message in error, please contact your administrator.")
            return
        if event.key() not in (inc.key() for inc in org_by_id.incidents):
            self.redirect("organization-info?message=The organization you are trying to view doesn't belong to the event that you are signed in to. If you think you are seeing this message in error, please contact your administrator.")
            return
        org_key = org_by_id.key()
        
        contact_query = db.GqlQuery(
            "SELECT * From Contact WHERE organization = :org_key",
            org_key=org_key
        )

        return self.render(
            template='organization_info.html',
            organization=org_by_id,
            contacts=contact_query,
            is_admin=org_by_id.is_admin,
            message=message
        )
