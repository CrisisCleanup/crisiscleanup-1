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
import jinja2
import os
from google.appengine.ext import db
from urlparse import urlparse


# Local libraries.
import base
import event_db
import primary_contact_db
import organization
import key
import page_db
import random_password
import messaging


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('new_organization.html')


class NewOrganizationHandler(base.RequestHandler):

    CONTACT_PROPERTIES_LIST = ["first_name", "last_name", "title", "personal_phone", "personal_email"]

    BOOLEAN_PROPERTIES_LIST = [
        "publish",
        "physical_presence",
        "appropriate_work",
        "voad_member",
        "does_recovery",
        "does_only_coordination",
        "does_only_sit_aware",
        "does_something_else",
        "not_an_org",
        "reputable",
        "physical_presence"
    ]

    def get(self):
	logged_in = False
        org, event = key.CheckAuthorization(self.request)
        if org and key:
	  logged_in = True
        events_list = db.GqlQuery("SELECT * FROM Event ORDER BY created_date DESC")

        template_params = page_db.get_page_block_dict()
        template_params.update({
	    "logged_in": logged_in,
            "events_list": events_list,
        })
        self.response.out.write(template.render(template_params))
        
    def post(self):
        # create inactive, unverified org with a random password
        org = organization.Organization(
            name=self.request.get("name"),
            is_active=False,
            org_verified=False,
            voad_referral=self.request.get("voad_referral"),
            password=random_password.generate_password()
        )

        # set non-contact org attributes by type
	for k, v in self.request.POST.iteritems():
          if not any(k.startswith(prop) for prop in self.CONTACT_PROPERTIES_LIST):
	    if k == "choose_event":
	      chosen_event = event_db.Event.get_by_id(int(v))
	      setattr(org, "incidents", [chosen_event.key()])
	    elif k in self.BOOLEAN_PROPERTIES_LIST:
	      setattr(org, k, bool(int(v)))
	    else:
              # clean away known pre-supplied strings
              if v.strip() in ('http://', '@'):
                  v = None
	      setattr(org, k, v)

        # create contacts
        def get_contact_field(field_name, contact_num):
            field_value = self.request.get(field_name + '_%d' % i)
            return field_value.strip() if field_value else None

        new_contacts = []

        for i in range(10):
            first_name = get_contact_field('first_name', i)
            last_name = get_contact_field('last_name', i)
            title = get_contact_field('title', i)
            email = get_contact_field('personal_email', i)
            phone = get_contact_field('personal_phone', i)

            if first_name and last_name and email and phone:  # required fields
                new_contacts.append(primary_contact_db.Contact(
                    first_name=first_name,
                    last_name=last_name,
                    title=title,
                    email=email,
                    phone=phone,
                    is_primary=(i == 0)  # the first contact is the primary one
                ))

        # save
	organization.PutAndCacheOrganizationAndContact(org, new_contacts)

        # email primary contacts & administrators
        organization_form = organization.OrganizationForm(None, org)
        contact_forms = [
            primary_contact_db.ContactFormFull(None, contact)
            for contact in new_contacts
        ]
        messaging.email_contacts_using_templates(
            event=chosen_event,
            contacts=[c for c in new_contacts if c.is_primary],
            subject_template_name='new_organization.to_contacts.subject.txt',
            body_template_name='new_organization.to_contacts.body.txt',
            new_organization=org,
            primary_contact=new_contacts[0],
            application_id=messaging.get_application_id(),
            organization_form=organization_form,
            contact_forms=contact_forms,
        )
        approval_url = "%s://%s/admin-new-organization?new_organization=%d" % (
            urlparse(self.request.url).scheme,
            urlparse(self.request.url).netloc,
            org.key().id()
        )
        messaging.email_administrators_using_templates(
            event=chosen_event,
            subject_template_name='new_organization.to_admins.subject.txt',
            body_template_name='new_organization.to_admins.body.txt',
            new_organization=org,
            primary_contact=new_contacts[0],
            application_id=messaging.get_application_id(),
            approval_url=approval_url,
            organization_form=organization_form,
            contact_forms=contact_forms,
        )
			    
	self.redirect("/welcome")
