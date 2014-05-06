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

# Local libraries
import base
import site_db
import event_db

import datetime

PAGE_OFFSET = 100

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class HomeUserMapAjaxHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        event_shortname = self.request.get("shortname")
        page = self.request.get("page")
        page_int = int(page)

        county_and_state = self.request.get("county_and_state")
        work_type = self.request.get("work_type")
        date_from = self.request.get("date_from")
        date_to = self.request.get("date_to")




        if event_shortname == None:
            event_shortname = "sandy"
        event = None
        events = event_db.GetAllCached()
        for e in events:
            if e.short_name == event_shortname:
                event = e


        #ids = []
        #where_string = "Open"
        #q = None

        #if event.short_name != 'moore':
        #    gql_string = 'SELECT * FROM Site WHERE status >= :1 and event = :2'
        #    q = db.GqlQuery(gql_string, where_string, event.key())

        #else:

        q = Query(model_class = site_db.Site)

        q.filter('reported_by', org.key())
        q.filter("event =", event.key())
        q.is_keys_only()
        q.filter("status IN", ["Open, unassigned", "Open, assigned", "Open, partially completed", "Open, needs follow-up"])

        if county_and_state:
            site_proj = Query(
                model_class = site_db.Site,
                projection=('county', 'state'),
                distinct=True
            )
            site_proj.filter("event =", event.key())
            site_proj.filter("reported_by =", org.key())

            counties_and_states = {
                site.county_and_state : (site.county, site.state) for site
                in site_proj
            }
            county, state = counties_and_states[county_and_state]
            q.filter('county', county).filter('state', state)
        if work_type:
            q.filter('work_type IN', work_type.split(','))
        if date_from:
            q.filter('request_date >=', datetime.datetime.strptime(date_from, '%m/%d/%Y').date())
        if date_to:
            q.filter('request_date <', (datetime.datetime.strptime(date_to, '%m/%d/%Y')+datetime.timedelta(days=1)).date())

        this_offset = page_int * PAGE_OFFSET

        ids = [key.key().id() for key in q.fetch(PAGE_OFFSET, offset = this_offset)]

        def public_site_filter(site):
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
                }

        output = json.dumps(
            [public_site_filter(s[1]) for s in site_db.GetAllCached(event, ids)],
            default=dthandler
        )
        self.response.out.write(output)
