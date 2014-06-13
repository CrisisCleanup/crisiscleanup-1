#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
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
import datetime
import json
from google.appengine.ext import db
from google.appengine.ext.db import Query

from google.appengine.api.datastore import Key

# Local libraries
import base
import site_db
import event_db
import campaign_db

import logging

import datetime

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class CampaignViewMapAjaxHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        page = self.request.get("page")
        page_int = int(page)

        campaign_id = int(self.request.get("campaign_id"))

        q = Query(model_class = site_db.Site)

        q.filter('reported_by', org.key())
        q.filter("event =", event.key())
        q.is_keys_only()
        q.filter("status IN", ["Open, unassigned", "Open, assigned", "Open, partially completed", "Open, needs follow-up"])

        if campaign_id:
            campaign = campaign_db.Campaign.get_by_id(campaign_id)
            q.filter("campaign =", campaign.key())

        this_offset = page_int * PAGE_OFFSET

        ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]

        def public_site_filter(site):
            logging.info(site)
            # site as dict
            return {
                'event': site['event'],
                'id': site['id'],
                'case_number': site['case_number'],
                'work_type': site['work_type'],
                'claimed_by': site['claimed_by'],
                'status': site['status'],
                'floors_affected': site.get('floors_affected'),
                'blurred_latitude': site.get('blurred_latitude'),
                'blurred_longitude': site.get('blurred_longitude'),
                'answer1': site['answer1'],
                'answer2': site['answer2'],
                'answer3': site['answer3'],
                'answer4': site['answer4'],
                'answer5': site['answer5'],
                'answer1_correct': site['answer1_correct'],
                'answer2_correct': site['answer2_correct'],
                'answer3_correct': site['answer3_correct'],
                'answer4_correct': site['answer4_correct'],
                'answer5_correct': site['answer5_correct'],
                }

        output = json.dumps(
            [public_site_filter(s[1]) for s in site_db.GetAllCached(event, ids)],
            default=dthandler
        )
        self.response.out.write(output)
