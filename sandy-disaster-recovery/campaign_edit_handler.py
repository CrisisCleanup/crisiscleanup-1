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
from campaign_db import Campaign

import organization


class CampaignEditHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'campaign_edit.html'

    def AuthenticatedGet(self, authenticated_org, event):
        # get & check campaign
        try:
            id = int(self.request.get("campaign"))
            campaign = campaign_db.Campaign.get_by_id(id)
            if campaign.organization.key() != authenticated_org.key():
                self.abort(403)
        except:
            self.abort(404)

        # cannot edit when there is answers of questions
        count_answers = campaign_db.Campaign.count_answers(campaign)

        # construct form
        form = campaign_db.CampaignForm(None, campaign)
        return self.render(
            edit_campaign_id=id,
            form=form,
            count_answers=count_answers
        )


    def AuthenticatedPost(self, authenticated_org, event):
        form = campaign_db.CampaignForm(self.request.POST)
        try:
            id = int(self.request.get("campaign"))
            campaign = campaign_db.Campaign.get_by_id(id)
            if campaign.organization.key() != authenticated_org.key():
                self.abort(403)
        except:
            self.abort(404)

        if (campaign_db.Campaign.count_answers(campaign)>0):
            self.abort(403)

        # validate form and save if successful
        if form.validate():
            form.populate_obj(campaign)
            campaign.put()
            return self.redirect("/campaigns-index")
        else:
            return self.render(
                form=form,
                )
