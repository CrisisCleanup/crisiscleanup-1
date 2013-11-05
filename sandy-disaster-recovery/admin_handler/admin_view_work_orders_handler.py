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

from google.appengine.ext.db import Query, Key

from wtforms import Form, TextField, HiddenField, SelectField
from wtforms.ext.appengine.fields import ReferencePropertyField

from admin_base import AdminAuthenticatedHandler

import event_db
from site_db import Site
from organization import Organization


class WorkOrderSearchForm(Form):

    offset = HiddenField(default="0")
    order = HiddenField()
    event = SelectField(default='')
    query = TextField("Search")
    reporting_org = ReferencePropertyField(
        reference_class=Organization,
        label_attr='name',
        allow_blank=True
    )
    claiming_org = ReferencePropertyField(
        reference_class=Organization,
        label_attr='name',
        allow_blank=True
    )
    work_type = SelectField(default='')  # dynamic
    status = SelectField(
        choices=[('', '')] + [
            (s, s) for s in Site.status.choices
        ],
        default=''
    )
    per_page = SelectField(
        choices=[
            (n, n) for n in [10, 50, 100, 500]
        ],
        coerce=int,
        default=10
    )


class AdminViewWorkOrdersHandler(AdminAuthenticatedHandler):

    template = "admin_view_work_orders.html"

    def AuthenticatedGet(self, org, event):
        form = WorkOrderSearchForm(self.request.GET)

        # get relevant organizations and incidents
        if org.is_global_admin:
            events = event_db.Event.all()
            query = Site.all()
            work_types = [
                site.work_type for site 
                in Query(Site, projection=['work_type'], distinct=True)
            ]
        elif org.is_local_admin:
            events = [event_db.Event.get(org.incident.key())]
            query = Site.all().filter('event', org.incident.key())
            work_types = [
                site.work_type for site
                in Query(Site, projection=['work_type'], distinct=True) \
                    .filter('event', org.incident.key())
            ]

        # set form choices
        form.event.choices = [('', '')] + [
            (e.key(), e.name) for e in events
        ]
        form.work_type.choices = [('', '')] + [
            (work_type, work_type) for work_type in work_types
        ]

        # validate form
        form.validate()

        # begin constructing query 
        query = Site.all()

        # if a local admin, filter to logged in event
        if org.is_local_admin:
            query.filter('event', event.key())

        # apply filters if set 
        if form.event.data:
            query.filter('event', Key(form.event.data))
        if form.reporting_org.data:
            query.filter('reported_by', form.reporting_org.data)
        if form.claiming_org.data:
            query.filter('claimed_by', form.claiming_org.data)
        if form.work_type.data:
            query.filter('work_type', form.work_type.data)
        if form.status.data:
            query.filter('status', form.status.data)

        # apply order
        if form.order.data:
            query.order(form.order.data)

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
