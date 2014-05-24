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

import os
import jinja2
from google.appengine.ext.db import Key
import event_db

# Local libraries.
import base
import organization
from organization import OrganizationForm, GlobalAdminOrganizationForm
from primary_contact_db import Contact, ContactFormFull, ContactFormFullWithDelete


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_edit_org.html')


class AdminEditOrganizationHandler(base.AuthenticatedHandler):

    def _get_forms(self, post_data, authenticated_org, org_by_id, incidents):
        """
        Construct an organization form, a contact form for each existing
        contact and also 10 blank contact forms for potential new contacts.

        Note: sets form field prefixes to allow multiple forms in one request.
        """
        organization_form = (
            GlobalAdminOrganizationForm(
                post_data, org_by_id, incidents=incidents, prefix='org-')
            if authenticated_org.is_global_admin
            else OrganizationForm(
                post_data, org_by_id, incidents=incidents, prefix='org-')
        )
        existing_contact_forms = [
            ContactFormFullWithDelete(
                post_data, contact, id=contact.key().id(),
                prefix="contact-%d-" % contact.key().id()
            )
            for contact in org_by_id.contacts.order('-is_primary')
        ]
        blank_contact_forms = [
            ContactFormFull(post_data, prefix="new-contact-%d" % i)
            for i in range(10)
        ]
        return organization_form, existing_contact_forms, blank_contact_forms

    def AuthenticatedGet(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        try:
            org_by_id = organization.Organization.get_by_id(
                int(self.request.get("organization"))
            )
        except:
            self.abort(404)
            
        # bail if not allowed
        if not org.may_administer(org_by_id):
            self.abort(403)

        # construct forms
        organization_form, existing_contact_forms, blank_contact_forms = \
            self._get_forms(None, org, org_by_id, None)

	incidents = event_db.Event.all()
        self.response.out.write(template.render({
            "organization": org_by_id,
            "organization_form": organization_form,
            "existing_contact_forms": existing_contact_forms,
            "blank_contact_forms": blank_contact_forms,
            "incidents": incidents
        }))

    def AuthenticatedPost(self, org, event):
        if not (org.is_global_admin or org.is_local_admin):
            self.abort(403)

        try:
            org_by_id = organization.Organization.get_by_id(
                int(self.request.get("organization"))
            )
        except:
            self.abort(404)

        # bail if not allowed
        if not org.may_administer(org_by_id):
            self.abort(403)

        # construct forms
        incidents = [
            # hack to workaround apparent bug in webapp2 re multiple selects
            Key(v) for k,v in self.request.POST.items()
            if k.startswith('incidents')
        ]
        organization_form, existing_contact_forms, blank_contact_forms = \
            self._get_forms(self.request.POST, org, org_by_id, incidents)

        # remove unused blank contact forms
        blank_contact_forms = filter(lambda f: any(f.data.values()), blank_contact_forms)
        for bcf in blank_contact_forms:
            bcf.has_data = True

        # validate forms
        all_forms = [organization_form] + existing_contact_forms + blank_contact_forms
        if all(form.validate() for form in all_forms):
            # update org
            organization_form.populate_obj(org_by_id)
            org_by_id.save()

            # update existing contacts
            existing_contacts = org_by_id.contacts
            for contact_form in existing_contact_forms:
                contact_form_id = \
                    int(contact_form.id.data) if contact_form.id.data else -1
                contact = [
                    ec for ec in existing_contacts
                    if ec.key().id() == contact_form_id 
                ][0]
                delete_requested = contact_form.delete_me.data
                if delete_requested:
                    contact.delete()
                else:
                    contact_form.populate_obj(contact)
                    contact.save()

            # create new
            for contact_form in blank_contact_forms:
                contact = Contact(
                    organization=org_by_id,
                    first_name=contact_form.first_name.data,
                    last_name=contact_form.last_name.data,
                    title=contact_form.title.data,
                    phone=contact_form.phone.data,
                    email=contact_form.email.data,
                    is_primary=contact_form.is_primary.data
                )
                contact.save()
            self.redirect('/admin-edit-organization?organization=%d' % org_by_id.key().id())
        else:
            self.response.out.write(template.render({
                "errors": True,
                "organization": org_by_id,
                "organization_form": organization_form,
                "existing_contact_forms": existing_contact_forms,
                "blank_contact_forms": blank_contact_forms,
            }))
