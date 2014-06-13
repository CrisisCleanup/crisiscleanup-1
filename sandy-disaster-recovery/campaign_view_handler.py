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
from site_db import Site
from campaign_db import Campaign

import logging

import organization


class CampaignEditHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'campaign_view.html'

    def AuthenticatedGet(self, authenticated_org, event):
        # get & check campaign
        try:
            id = int(self.request.get("campaign"))
            campaign = campaign_db.Campaign.get_by_id(id)
            if campaign.organization.key() != authenticated_org.key():
                self.abort(403)
            query = Site.all().filter('campaign', campaign.key())
            sites = list(query.run())
        except:
            self.abort(404)

        questions = {1: {'question': campaign.question1}, 2: {'question': campaign.question2}, 3: {'question': campaign.question3}, 4: {'question': campaign.question4}, 5: {'question': campaign.question5}}
        for qid in questions:
            for site in sites:
                if getattr(site, 'answer'+str(qid)):
                    if 'answer_count' in questions[qid]:
                        questions[qid]['answer_count'] += 1
                    else:
                        questions[qid]['answer_count'] = 1
                    if 'correct' in questions[qid]:
                        questions[qid]['correct'] += int(getattr(site, 'answer'+str(qid)+'_correct'))
                    else:
                        questions[qid]['correct'] = int(getattr(site, 'answer'+str(qid)+'_correct'))

        # construct form
        form = campaign_db.CampaignForm(None, campaign)
        return self.render(
            edit_campaign_id=id,
            campaign=campaign,
            questions=questions,
            form=form,
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
