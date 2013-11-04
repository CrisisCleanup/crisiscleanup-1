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

from admin_base import AdminAuthenticatedHandler

from site_db import Site
from organization import Organization

from wtforms import Form, TextField, SelectField
from wtforms.ext.appengine.fields import ReferencePropertyField


class WorkOrderSearchForm(Form):

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
    work_type = SelectField()  # dynamic
    status = SelectField(choices=[('', '')] + [
        (s, s) for s in Site.status.choices
    ])


class AdminViewWorkOrdersHandler(AdminAuthenticatedHandler):

    template = "admin_view_work_orders.html"

    def AuthenticatedGet(self, org, event):
        return self.AuthenticatedPost(org, event)

    def AuthenticatedPost(self, org, event):
        form = WorkOrderSearchForm(self.request.POST)
        form.work_type.choices = [('', '')] + [
            (site.work_type, site.work_type) for site 
            in Site.all(projection=['work_type'], distinct=True)
        ]
        form.validate()

        # begin constructing query 
        sites = Site.all()

        # if a local admin, filter to logged in event
        if org.is_local_admin:
            sites.filter('event', event.key())

        # apply filters if set 
        if form.reporting_org.data:
            sites.filter('reported_by', form.reporting_org.data)
        if form.claiming_org.data:
            sites.filter('claimed_by', form.claiming_org.data)
        if form.work_type.data:
            sites.filter('work_type', form.work_type.data)
        if form.status.data:
            sites.filter('status', form.status.data)

        # if search terms specified, naively search in multiple fields
        search_terms = self.request.get('q', '').strip().lower().split()
        if sites and search_terms:
            sites = [
                site for site in sites if any(
                    any(
                        term in field.lower() for field in [
                            site.name,
                            site.full_address,
                            site.reported_by.name,
                            site.claimed_by.name,
                        ]
                    ) for term in search_terms
                )
            ]

        self.render(
            form=form,
            sites=sites
        )
