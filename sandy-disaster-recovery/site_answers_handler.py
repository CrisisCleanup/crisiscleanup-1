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
import site_db

from wtforms import Form, IntegerField, SelectField, TextField, HiddenField, widgets

from campaign_db import Campaign

import organization

import logging

class SiteAnswersHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'site_answers.html'

    #   CONTINUE HERE !

    def AuthenticatedGet(self, authenticated_org, event):


        #get questions of campaign of this site
        try:
            id = int(self.request.get("id"))
            site = site_db.GetAndCache(int(id))
            if not site:
                self.response.set_status(404)
                return
            campaign = campaign_db.Campaign.get(site.campaign.key())
            if campaign.organization.key() != authenticated_org.key():
                self.abort(403)
        except:
            self.abort(404)


        # construct answers form
        Form = create_answers_form(id, campaign)
        form = Form(obj=site)
        return self.render(
            id=id,
            form=form,
        )


    def AuthenticatedPost(self, authenticated_org, event):

        try:
            id = int(self.request.get("id"))
            site = site_db.GetAndCache(int(id))
            if not site:
                self.response.set_status(404)
                return
            campaign = campaign_db.Campaign.get(site.campaign.key())
            logging.info(campaign)
            if campaign.organization.key() != authenticated_org.key():
                self.abort(403)
        except:
            self.abort(404)

        Form = create_answers_form(id, campaign)
        form = Form(self.request.POST)

        if hasattr(form, 'answer1_correct'):
            form.answer1_correct.data = int(form.answer1_correct.data)
        if hasattr(form, 'answer2_correct'):
            form.answer2_correct.data = int(form.answer2_correct.data)
        if hasattr(form, 'answer3_correct'):
            form.answer3_correct.data = int(form.answer3_correct.data)
        if hasattr(form, 'answer4_correct'):
            form.answer4_correct.data = int(form.answer4_correct.data)
        if hasattr(form, 'answer5_correct'):
            form.answer5_correct.data = int(form.answer5_correct.data)

        # validate form and save if successful
        if form.validate():
            form.populate_obj(site)
            site.save()
            site_db.PutAndCache(site)
        return self.render(
            id=id,
            form=form,
            )



def create_answers_form(site_id, campaign):
    percentage_correct = [(p*10, str(p*10)+'%') for p in range(0, 11)]

    class AnswersForm(Form):
        if (campaign.question1):
            answer1 = TextField(label=campaign.question1)
            answer1_correct = SelectField(choices=percentage_correct,coerce=int)
        if (campaign.question2):
            answer2 = TextField(label=campaign.question2)
            answer2_correct = SelectField(choices=percentage_correct,coerce=int)
        if (campaign.question3):
            answer3 = TextField(label=campaign.question3)
            answer3_correct = SelectField(choices=percentage_correct,coerce=int)
        if (campaign.question4):
            answer4 = TextField(label=campaign.question4)
            answer4_correct = SelectField(choices=percentage_correct,coerce=int)
        if (campaign.question5):
            answer5 = TextField(label=campaign.question5)
            answer5_correct = SelectField(choices=percentage_correct,coerce=int)

    return AnswersForm
