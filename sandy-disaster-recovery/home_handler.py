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

# System libraries.
from google.appengine.ext import db

# Local libraries.
from wtforms import Form, IntegerField, SelectField, SelectMultipleField, TextField, widgets

import json

import base


import event_db
from site_db import Site

import datetime


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def create_site_filter_form(counties_and_states, work_type_options):

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
                #(u'name', u'Name (asc)'),
                #(u'-name', u'Name (desc)'),
                ],
            default=u'-request_date',
            )
        work_type = MultiCheckboxField(
            choices=[
                (cat_k, str((cat_k if cat_k != '' else 'None'))+' ('+str(cat_v)+')') for cat_k, cat_v in sorted(work_type_options.iteritems())
            ],
            )
        date_from = TextField(
            #format='%m/%d/%Y',
            )
        date_to = TextField(
            #format='%m/%d/%Y',
            )
        """
                (u'Health', u'Health'),
                (u'Hosting & Non-food products', u'Hosting & Non-food products'),
                (u'Food', u'Food'),
                (u'Water & Sanitation', u'Water & Sanitation'),
                (u'Education', u'Education'),
                (u'Jobs & Stands socio-economic', u'Jobs & Stands socio-economic'),
                (u'Protection & Security', u'Protection & Security'),
                (u'Infrastructure and logistics', u'Infrastructure and logistics'),
                (u'Various', u'Various'),
        """

    return SiteFilterForm


class HomeHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'home.html'

    SITES_PER_PAGE = 20

    def get(self):
        try:
            with open('version.json') as version_json_fd:
                version_d = json.load(version_json_fd)
        except:
            version_d = None

        # events for map
        events = event_db.GetAllCached()


        site_proj = db.Query(
            Site,
            projection=('county', 'state'),
            distinct=True
        )
        counties_and_states = {
            site.county_and_state : (site.county, site.state) for site
            in site_proj
        }

        #count messages in work_type (categories)
        # count messages for chart
        work_type_options_tmp = {}
        chart_messages = {}
        for site in db.GqlQuery('SELECT work_type, request_date FROM Site ORDER BY request_date'):
            if site.work_type in work_type_options_tmp:
                work_type_options_tmp[site.work_type] += 1
            else:
                work_type_options_tmp[site.work_type] = 1
            tmp_request_date = site.request_date.strftime('%Y, %m, %d');
            if tmp_request_date in chart_messages:
                chart_messages[tmp_request_date] += 1
            else:
                chart_messages[tmp_request_date] = 1

        work_type_options = {
            cat_k: cat_v for cat_k , cat_v
            in work_type_options_tmp.iteritems()
        }

        Form = create_site_filter_form(counties_and_states, work_type_options)
        form = Form(self.request.GET)
        #import pdb; pdb.set_trace();
        if not form.validate():
            form = Form()  # => use defaults


        # construct query
        query = Site.all()
        query.filter("status IN", ["Open, unassigned", "Open, assigned", "Open, partially completed", "Open, needs follow-up"])
        if form.county_and_state.data:
            county, state = counties_and_states[form.county_and_state.data]
            query = query.filter('county', county).filter('state', state)
        if form.order.data:
            query = query.order(form.order.data)
        else:
            query = query.order('-request_date')
        if form.work_type.data:
            query = query.filter('work_type IN', form.work_type.data)
        if form.date_from.data:
            query = query.filter('request_date >=', datetime.datetime.strptime(form.date_from.data, '%m/%d/%Y').date())
        if form.date_to.data:
            query = query.filter('request_date <', (datetime.datetime.strptime(form.date_to.data, '%m/%d/%Y')+datetime.timedelta(days=1)).date())

        # run query
        sites = list(query.run(
            offset=form.page.data * self.SITES_PER_PAGE,
            limit=self.SITES_PER_PAGE
        ))


        self.render(
            events=events,
            version_d=version_d,
            form=form,
            sites=sites,
            sites_per_page=self.SITES_PER_PAGE,
            chart_messages=chart_messages,
        )


