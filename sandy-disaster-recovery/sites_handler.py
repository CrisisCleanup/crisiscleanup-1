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
from google.appengine.ext import db

# Local libraries.
from wtforms import Form, IntegerField, SelectField, widgets

import base
from site_db import Site


def create_site_filter_form(counties_and_states):

    class SiteFilterForm(Form):

        page = IntegerField(default=0, widget=widgets.HiddenInput())
        county_and_state = SelectField(
            choices=[(u'', u'(All)')] + [
                (cas, cas) for cas in sorted(counties_and_states)
            ],
            default=u'',
        )
        order = SelectField(
            choices=[
                (u'-request_date', u'Request Date (recent first)'),
                (u'request_date', u'Request Date (oldest first)'),
                (u'name', u'Name (asc)'),
                (u'-name', u'Name (desc)'),
            ],
            default=u'-request_date',
        )

    return SiteFilterForm


class SitesHandler(base.FrontEndAuthenticatedHandler):
    
    SITES_PER_PAGE = 200

    template_filename = 'sites.html'

    def AuthenticatedGet(self, org, event):
        site_proj = db.Query(
            Site,
            projection=('county', 'state'),
            distinct=True
        ).filter('event', event)
        counties_and_states = {
            site.county_and_state : (site.county, site.state) for site
            in site_proj
        }
        Form = create_site_filter_form(counties_and_states)
        form = Form(self.request.GET)
        if not form.validate():
            form = Form()  # => use defaults

        # construct query
        query = Site.all().filter('event', event.key())
        if form.county_and_state.data:
            county, state = counties_and_states[form.county_and_state.data]
            query = query.filter('county', county).filter('state', state)
        if form.order.data:
            query = query.order(form.order.data)

        # run query
        sites = list(query.run(
            offset=form.page.data * self.SITES_PER_PAGE,
            limit=self.SITES_PER_PAGE
        ))

        return self.render(
            form=form,
            sites=sites,
            sites_per_page=self.SITES_PER_PAGE,
        )
