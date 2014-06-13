#!/usr/bin/env python
#
# Copyright 2014 Nicolas Zanghi
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
import campaign_db
import organization


import time

class CampaignAddHandler(base.FrontEndAuthenticatedHandler):
    template_filename = 'campaign_add.html'

    def AuthenticatedGet(self, org, event):
        form = campaign_db.CampaignForm()

        return self.render(
            form=form,
        )

    def AuthenticatedPost(self, org, event):
        form = campaign_db.CampaignForm(self.request.POST)
        org_id = org.key().id()
        try:
            id = int(org_id)
            org = organization.Organization.get_by_id(id)
        except:
            return

        # validate form and save if successful
        if form.validate():
            campaign = campaign_db.Campaign(
                name=form.name.data,
                question1=form.question1.data,
                question2=form.question2.data,
                question3=form.question3.data,
                question4=form.question4.data,
                question5=form.question5.data,
                organization=org.key(),
            )
            campaign.put()
            time.sleep(0.1)
            return self.redirect("/campaigns-index")
        else:
            return self.render(
                form=form,
            )
