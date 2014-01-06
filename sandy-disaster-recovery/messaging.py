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

import os

from google.appengine.api import app_identity, mail

import jinja2

from admin_handler.admin_identity import get_global_admins, get_event_admins


# jinja

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'email_templates'
        )
    )
)


# constants

APP_ID_TO_SENDER_ADDRESS = {
    'sandy-helping-hands': 'CrisisCleanup <help@crisiscleanup.org>',
    'sandy-disaster-recovery': 'CrisisCleanup <help@crisiscleanup.org>',
    'crisis-cleanup-au': 'CrisisCleanup <help@crisiscleanup.org.au>',
    'crisis-cleanup-in': 'CrisisCleanup <help@crisiscleanup.org.in>',
}


# functions

def get_application_id():
    return app_identity.get_application_id()


def get_default_version_hostname():
    return app_identity.get_default_version_hostname()


def get_app_system_email_address():
    app_id = app_identity.get_application_id()
    # HOTFIX START
    return (
        "%s <noreply@%s.appspotmail.com>" % (
            app_identity.get_service_account_name(),
            app_identity.get_application_id()
        )
    )
    # HOTFIX END
    return APP_ID_TO_SENDER_ADDRESS.get(
        # by app id
        app_id,

        # or else use default
        "%s <noreply@%s.appspotmail.com>" % (
            app_identity.get_service_account_name(),
            app_identity.get_application_id()
        )
    )


def email_administrators(event, subject, body, html=None, include_local=True):
    prefixed_subject = "[%s] %s" % (app_identity.get_application_id(), subject)
    sender_address = get_app_system_email_address()

    admin_orgs = get_event_admins(event) if include_local else get_global_admins()

    for admin_org in admin_orgs:
        for contact in admin_org.primary_contacts:
            if contact.email:
                recipient_address = "%s <%s>" % (contact.email, contact.full_name)
                mail_args = {
                    'sender': sender_address,
                    'to': recipient_address,
                    'subject': prefixed_subject,
                    'body': body,
                }
                if html:
                    mail_args['html'] = html
                mail.send_mail(**mail_args)


def email_administrators_using_templates(
    event, subject_template_name, body_template_name, **kwargs):
    """
    Email all relevant administrators for event, using Jinja2 templates.
    """
    subject_template = jinja_environment.get_template(subject_template_name)
    body_template = jinja_environment.get_template(body_template_name)

    kwargs.update({'event': event})

    rendered_subject = subject_template.render(kwargs)
    rendered_body = body_template.render(kwargs)

    email_administrators(event, rendered_subject, rendered_body)



import base
import key

GLOBAL_ADMIN_NAME = "Admin"

class EmailTestHandler(base.RequestHandler):

    def get(self):
        org, event = key.CheckAuthorization(self.request)
	if not (org and org.name == GLOBAL_ADMIN_NAME):
            self.response.out.write("Must be global admin.")
            return

        to_addr = self.request.get("to")
        from_addr = self.request.get("from")

        if to_addr and from_addr:
            mail.send_mail(
                from_addr,
                to_addr,
                "Test email",
                "This is a test email."
            )
            self.response.out.write("Test email sent.")
        else:
            self.response.out.write("Need to and from addresses")
