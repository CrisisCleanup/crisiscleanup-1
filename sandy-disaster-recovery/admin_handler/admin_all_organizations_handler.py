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
#
# System libraries.
from wtforms import Form, TextField, IntegerField, SelectField

# Local libraries.
from admin_base import AdminAuthenticatedHandler
import organization


class OrganizationFilterForm(Form):

    def _ternary_coerce(val):
        return {'1': True, '0': False}.get(val, None)

    name = TextField()
    active = SelectField(
        choices=[('', ''), ('1', 'Yes'), ('0', 'No')],
        coerce=_ternary_coerce
    )
    verified = SelectField(
        choices=[('', ''), ('1', 'Yes'), ('0', 'No')],
        coerce=_ternary_coerce
    )
    logged_in_days = IntegerField()


class AdminAllOrgsHandler(AdminAuthenticatedHandler):

    template = 'admin_all_organizations.html'

    def AuthenticatedGet(self, org, event):
        form = OrganizationFilterForm(self.request.GET)

        # get relevant organizations
        if org.is_global_admin:
            query = organization.Organization.all()
            
        if org.is_local_admin:
            query = organization.Organization.all().filter('incident', org.incident.key())

        # filter on active/inactive
        if form.active.data is not None:
            query.filter('is_active', form.active.data)
        if form.verified.data is not None:
            query.filter('is_verified', form.verified.data)

        self.render(
            form=form,
            org_query=query,
            url="/admin-single-organization?organization=",
            global_admin=org.is_global_admin,
        )
