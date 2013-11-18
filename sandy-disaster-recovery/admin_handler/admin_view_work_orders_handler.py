#!/usr/bin/env python
#
# Copyright 2013 Chris Wood 
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

import pickle

from google.appengine.ext.db import Query, Key

from wtforms import Form, TextField, HiddenField, SelectField

from admin_base import AdminAuthenticatedHandler

import event_db
from site_db import Site
from organization import Organization
from export_bulk_handler import AbstractExportBulkHandler, AbstractExportBulkWorker


def create_work_order_search_form(events, work_types):

    # filter orgs on selected events
    orgs = Organization.all().filter('incident in', [event for event in events])
    events_by_recency = sorted(events, key=lambda event: event.key().id(), reverse=True)

    class WorkOrderSearchForm(Form):

        offset = HiddenField(default="0")
        order = HiddenField()
        event = SelectField(
            choices=[
                (e.key(), e.name) for e in events_by_recency
            ],
            default=events_by_recency[0].key()
        )
        query = TextField("Search")
        reporting_org = SelectField(
            choices=[('', '')] + [
                (org.key(), org.name) for org in orgs
            ],
            default=''
        )
        claiming_org = SelectField(
            choices=[('', '')] + [
                (org.key(), org.name) for org in orgs
            ],
            default=''
        )
        work_type = SelectField(
            choices=[('', '')] + [
                (work_type, work_type) for work_type in work_types
            ],
            default=''
        )
        status = SelectField(
            choices=[('', '')] + [
                (s, s) for s in Site.status.choices
            ],
            default=''
        )
        per_page = SelectField(
            choices=[
                (n, n) for n in [10, 50, 100, 250]
            ],
            coerce=int,
            default=10
        )

    return WorkOrderSearchForm


def setup_and_query_from_form(org, event, form):
    # start query based on admin type
    if org.is_global_admin:
        query = Site.all()
    elif org.is_local_admin:
        query = Site.all().filter('event', org.incident.key())
    else:
        raise Exception("Not an admin")

    # validate form
    form.validate()

    # if a local admin, filter to logged in event
    if org.is_local_admin:
        query.filter('event', event.key())

    # apply filters if set 
    if form.event.data:
        query.filter('event', Key(form.event.data))
    if form.reporting_org.data:
        query.filter('reported_by', Key(form.reporting_org.data))
    if form.claiming_org.data:
        query.filter('claimed_by', Key(form.claiming_org.data))
    if form.work_type.data:
        query.filter('work_type', form.work_type.data)
    if form.status.data:
        query.filter('status', form.status.data)

    # apply order
    if form.order.data:
        query.order(form.order.data)

    return query


class AdminViewWorkOrdersHandler(AdminAuthenticatedHandler):

    template = "admin_view_work_orders.html"

    def AuthenticatedGet(self, org, event):
        # get relevant values for search form 
        if org.is_global_admin:
            events = event_db.Event.all()
            work_types = [
                site.work_type for site 
                in Query(Site, projection=['work_type'], distinct=True)
            ]
        elif org.is_local_admin:
            events = [event_db.Event.get(org.incident.key())]
            work_types = [
                site.work_type for site
                in Query(Site, projection=['work_type'], distinct=True) \
                    .filter('event', org.incident.key())
            ]

        WorkOrderSearchForm = create_work_order_search_form(
            events=events, work_types=work_types)
        form = WorkOrderSearchForm(self.request.GET)

        query = setup_and_query_from_form(org, event, form)

        # page using offset
        count = query.count(limit=1000000)
        offset = int(self.request.get('offset', 0))
        per_page = form.per_page.data
        sites = query.fetch(
            limit=per_page,
            offset=offset,
        )

        self.render(
            request=self.request,
            form=form,
            sites=sites,
            count=count,
            offset=offset,
            prev_offset=offset - per_page,
            next_offset=offset + per_page,
        )


class AdminExportWorkOrdersBulkHandler(AdminAuthenticatedHandler, AbstractExportBulkHandler):

    def AuthenticatedGet(self, org, event):
        raise Exception("Not supported")

    def AuthenticatedPost(self, org, event):
        self.org = org
        self.event = event
        self.start_export(org, event, '/admin-export-bulk-worker')
    
    def get_continuation_param_dict(self):
        d = super(AdminExportWorkOrdersBulkHandler, self).get_continuation_param_dict()
        d['org_pickle'] = pickle.dumps(self.org)
        d['event_pickle'] = pickle.dumps(self.event)
        d['post_pickle'] = pickle.dumps(self.request.POST)
        return d


class AdminExportWorkOrdersBulkWorker(AbstractExportBulkWorker):

    def get_base_query(self):
        org = pickle.loads(self.org_pickle)
        event = pickle.loads(self.event_pickle)
        post_data = pickle.loads(self.post_pickle)

        if org.is_global_admin:
            events = event_db.Event.all()
            work_types = [
                site.work_type for site 
                in Query(Site, projection=['work_type'], distinct=True)
            ]
        elif org.is_local_admin:
            events = [event_db.Event.get(org.incident.key())]
            work_types = [
                site.work_type for site
                in Query(Site, projection=['work_type'], distinct=True) \
                    .filter('event', org.incident.key())
            ]

        WorkOrderSearchForm = create_work_order_search_form(
            events=events, work_types=work_types)
        form = WorkOrderSearchForm(post_data)
        query = setup_and_query_from_form(org, event, form)
        return query

    def filter_sites(self, fetched_sites):
        return fetched_sites

    def get_continuation_param_dict(self):
        d = super(AdminExportWorkOrdersBulkWorker, self).get_continuation_param_dict()
        d['org_pickle'] = self.org_pickle
        d['event_pickle'] = self.event_pickle
        d['post_pickle'] = self.post_pickle
        return d 

    def post(self):
        self.org_pickle = self.request.get('org_pickle')
        self.event_pickle = self.request.get('event_pickle')
        self.post_pickle = self.request.get('post_pickle')
        super(AdminExportWorkOrdersBulkWorker, self).post()
