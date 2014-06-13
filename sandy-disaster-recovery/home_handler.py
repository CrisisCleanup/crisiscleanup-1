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

from google.appengine.api.datastore import Key

# Local libraries.
from wtforms import Form, IntegerField, SelectField, SelectMultipleField, TextField, BooleanField, widgets

import json

import base

import collections

import event_db
from site_db import Site

import datetime
from dateutil.relativedelta import relativedelta


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def create_site_filter_form(counties_and_states, states, counties, cities, work_type_options):

    class SiteFilterForm(Form):

        page = IntegerField(default=0, widget=widgets.HiddenInput())
        county_and_state = SelectField(
            choices=[(u'', u'(All)')] + [
                (cas, cas) for cas in sorted(counties_and_states)
            ],
            default=u'',
            )
        state = SelectField(
            choices=[(u'', u'(All)')] + [
                (s, s) for s in sorted(states)
            ],
            default=u'',
            )
        county = SelectField(
            choices=[(u'', u'(All)')] + [
                (c, c) for c in sorted(counties)
            ],
            default=u'',
            )
        city = SelectField(
            choices=[(u'', u'(All)')] + [
                (c, c) for c in sorted(cities)
            ],
            default=u'',
            )
        order = SelectField(
            choices=[
                (u'-request_date', u'Request Date (recent first)'),
                (u'request_date', u'Request Date (oldest first)'),
                (u'work_type', u'Category (asc)'),
                (u'-work_type', u'Category (desc)'),
                (u'message_type', u'Type (asc)'),
                (u'-message_type', u'Type (desc)'),
                (u'state', u'Region (asc)'),
                (u'-state', u'Region (desc)'),
                (u'county', u'Town (asc)'),
                (u'-county', u'Town (desc)'),
                (u'city', u'City (asc)'),
                (u'-city', u'City (desc)'),
                ],
            default=u'-request_date',
            )
        work_type = MultiCheckboxField(
            choices=[
                (cat_k, str('<img src="/icons/'+cat_k+'_black.png">'+(cat_k if cat_k != '' else 'None'))+' ('+str(cat_v)+')') for cat_k, cat_v in sorted(work_type_options.iteritems())
            ],
            )
        cccm = BooleanField()
        date_from = TextField(
            default = (datetime.date.today()+relativedelta(months=-1)).strftime('%m/%d/%Y')
            #format='%m/%d/%Y',
            )
        date_to = TextField(
            default = (datetime.date.today()).strftime('%m/%d/%Y')
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

        # on the public home get iom messages only
        iom_key = Key('ahNzfmNyaXNpcy1jbGVhbnVwLXBochkLEgxPcmdhbml6YXRpb24YgICAgOCwhQoM')
        #iom_key = Key('ahVkZXZ-Y3Jpc2lzLWNsZWFudXAtcGhyGQsSDE9yZ2FuaXphdGlvbhiAgICAgMCvCQw') # local nico

        site_state = db.Query(Site, projection=('county', 'state'))
        site_state.filter('reported_by', iom_key)

        site_county = db.Query(Site, projection=('city', 'county'))
        site_county.filter('reported_by', iom_key)

        site_city = db.Query(Site, projection=('name', 'city'))
        site_city.filter('reported_by', iom_key)

        if self.request.get('state'):
            site_county.filter('state', self.request.get('state'))
            site_city.filter('state', self.request.get('state'))

        if self.request.get('county'):
            site_city.filter('county', self.request.get('county'))

        counties_and_states = {}
        #counties_and_states = {
        #    site.county_and_state: (site.county, site.state) for site
        #    in site_proj
        #}


        states = {
            site.state: site.state for site
            in site_state
        }
        counties = {
            site.county: site.county for site
            in site_county
        }
        cities = {
            site.city: site.city for site
            in site_city
        }

        #count messages in work_type (categories)
        # count messages for chart
        work_type_options_tmp = {}
        chart_messages = collections.OrderedDict()
        query = Site.all().filter('reported_by', iom_key)
        query = query.order('request_date')
        sites = list(query.run())
        for site in sites:
            #db.GqlQuery('SELECT work_type, request_date FROM Site ORDER BY request_date'):
            if site.work_type in work_type_options_tmp:
                work_type_options_tmp[site.work_type] += 1
            else:
                work_type_options_tmp[site.work_type] = 1
            tmp_request_date = site.request_date.strftime('%Y, (%m-1), %d');
            if tmp_request_date in chart_messages:
                chart_messages[tmp_request_date] += 1
            else:
                chart_messages[tmp_request_date] = 1

        work_type_options = {
            cat_k: cat_v for cat_k , cat_v
            in work_type_options_tmp.iteritems()
        }

        Form = create_site_filter_form(counties_and_states, states, counties, cities, work_type_options)
        form = Form(self.request.GET)
        #import pdb; pdb.set_trace();
        if not form.validate():
            form = Form()  # => use defaults


        # construct query
        query = Site.all().filter('reported_by', iom_key)
        query.filter("status IN", ["Open, unassigned", "Open, assigned", "Open, partially completed", "Open, needs follow-up"])


        #demo_event = event_db.GetEventFromParam(5838406743490560) # demo event
        #query = query.filter('event', demo_event)


        if form.county_and_state.data:
            county, state = counties_and_states[form.county_and_state.data]
            query = query.filter('county', county).filter('state', state)
        if form.state.data:
            query = query.filter('state', form.state.data)
        if form.county.data:
            query = query.filter('county', form.county.data)
        if form.city.data:
            query = query.filter('city', form.city.data)
        if form.work_type.data:
            query = query.filter('work_type IN', form.work_type.data)
        if form.cccm.data:
            query = query.filter('cccm', 'y')


        #Note: Because of the way the App Engine Datastore executes queries, if a query specifies inequality filters on a property and sort orders on other properties, the property used in the inequality filters must be ordered before the other properties.
        if form.order.data:
            query = query.order(form.order.data)
            form.date_to.data = ''
            form.date_from.data = ''
        else:
            query = query.order('-request_date')
            if form.date_from.data:
                query = query.filter('request_date >=', datetime.datetime.strptime(form.date_from.data, '%m/%d/%Y').date())
            else:
                query = query.filter('request_date >=', (datetime.date.today()+relativedelta(months=-1)))
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


