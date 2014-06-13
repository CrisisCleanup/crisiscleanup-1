
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form

from wtforms import TextField, HiddenField, validators

import organization
import logging

class Campaign(db.Model):
    organization = db.ReferenceProperty(organization.Organization)
    name = db.StringProperty(required=True)
    question1 = db.StringProperty(required=False)
    question2 = db.StringProperty(required=False)
    question3 = db.StringProperty(required=False)
    question4 = db.StringProperty(required=False)
    question5 = db.StringProperty(required=False)



    @classmethod
    def for_event(cls, event, org):
        " Return generator of campaigns for organizations of event. "
        return (
            campaign for campaign in Campaign.all().filter('organization =', org)
            if campaign.organization
        and campaign.organization.may_access(event)
        )

    def count_answers(campaign):
        q = db.GqlQuery("SELECT * FROM Site WHERE answer1 != '' and campaign=:1", campaign.key())
        return q.count()




class CampaignForm(model_form(Campaign, exclude=['organization'])):

    id = HiddenField()
    name = TextField('Name', [
        validators.Length(
            min=1, max=100,
            message = "Name must be between 1 and 100 characters")
    ])
    question1 = TextField('Question 1')
    question2 = TextField('Question 2')
    question3 = TextField('Question 3')
    question4 = TextField('Question 4')
    question5 = TextField('Question 5')



# get options and replace in inc_form for form_handler.py
def get_options(inc_form, event, org):
    if 'id="campaign"' in inc_form:
        options_campaign = '<option value=""></option>'
        for campaign in Campaign.for_event(event, org):
            options_campaign += '<option value="'+str(campaign.key().id())+'">'+campaign.name+'</option>'
        inc_form = inc_form.replace('<select id="campaign" name="campaign">', '<select id="campaign" name="campaign">'+options_campaign)
    return inc_form

