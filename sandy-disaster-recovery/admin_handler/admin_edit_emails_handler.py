#!/usr/bin/env python
#
# Copyright 2014 Chris Wood
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

from xml.sax.saxutils import unescape

import wtforms
from wtforms.ext.appengine.db import model_form

from admin_base import AdminAuthenticatedHandler
from messaging import EmailTemplate, EMAIL_DESCRIPTIONS_BY_NAME

from event_db import Event
from organization import Organization
from primary_contact_db import Contact


class EmailTemplateForm(model_form(EmailTemplate)):

    # override model_form
    name = None
    use_html = wtforms.BooleanField('Use HTML')


class AdminEditEmailsHandler(AdminAuthenticatedHandler):

    template = 'admin_edit_emails.html'
    accessible_to_local_admin = False

    def _generate_forms(self):
        for name, description in sorted(EMAIL_DESCRIPTIONS_BY_NAME.items()):
            email_template_entity = EmailTemplate.get_by_name(name)
            form = EmailTemplateForm(
                self.request.POST,
                email_template_entity,
                prefix=name,
            )
            form.description = description
            form.email_template = email_template_entity
            yield form

    def render(self, **kwargs):
        # augment args to template with entity classes
        # (to list properties)
        super(AdminEditEmailsHandler, self).render(**dict(kwargs,
            Event=Event,
            Organization=Organization,
            Contact=Contact,
        ))

    def AuthenticatedGet(self, org, event):
        forms = list(self._generate_forms())
        self.render(
            forms=forms
        )

    def AuthenticatedPost(self, org, event):
        # unescape POST to allow HTML in forms
        for k in self.request.POST.keys():
            self.request.POST[k] = unescape(self.request.POST[k])

        # validate forms
        forms = list(self._generate_forms())
        map(lambda form: form.validate(), forms)
        errors = any(bool(form.errors) for form in forms)

        if errors:
            # render forms again
            return self.render(
                forms=forms,
                errors=errors,
            )
        else:
            # save updated templates
            for form in forms:
                form.populate_obj(form.email_template)
                form.email_template.save()
            return self.render(
                forms=forms
            )
