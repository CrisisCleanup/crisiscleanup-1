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

import logging
import os

from google.appengine.api import app_identity, mail

import jinja2

from config_key_db import get_config_key

from admin_handler.admin_identity import get_global_admins, get_event_admins

import aws


# jinja

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'templates',
            'email'
        )
    )
)


# functions

def get_application_id():
    return app_identity.get_application_id()


def get_default_version_hostname():
    return app_identity.get_default_version_hostname()


def get_base_url():
    configured_base_url = get_config_key('system_base_url')
    if configured_base_url:
        return configured_base_url
    else:
        # return http as the scheme and assume requests redirected
        return "http://" + get_default_version_hostname()


def get_appengine_default_system_email_address():
    return "%s <noreply@%s.appspotmail.com>" % (
        app_identity.get_service_account_name(),
        app_identity.get_application_id()
    )


def get_aws_ses_default_system_email_address():
    " From configuration "
    return get_config_key('system_email_address')


def send_email_via_appengine(sender, to, subject, body, cc=None, bcc=None, html_body=None):
    send_mail_args = {
        'sender': sender,
        'to': to,
        'subject': subject,
        'body': body,
    }
    if cc:
        send_mail_args['cc'] = cc
    if bcc:
        send_mail_args['bcc'] = bcc
    if html_body:
        send_mail_args['html'] = html_body
    return mail.send_mail(**send_mail_args)


def send_email_via_aws_ses(
        sender, to, subject, body, cc=None, bcc=None, html_body=None,
        aws_ses_region=None,
        aws_ses_access_key_id=None,
        aws_ses_secret_access_key=None,
    ):
    return aws.ses_send_email(
        source=sender,
        to_addresses=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
        aws_region=aws_ses_region,
        aws_access_key_id=aws_ses_access_key_id,
        aws_secret_access_key=aws_ses_secret_access_key,
    )


def can_send_by_aws_ses(
        aws_ses_region,
        aws_ses_access_key_id,
        aws_ses_secret_access_key,
        sender_address
    ):
    keys_available = bool(
        aws_ses_region and
        aws_ses_access_key_id and
        aws_ses_secret_access_key
    )
    if keys_available:
        verified_addresses = aws.ses_get_verified_email_addresses(
            aws_ses_region,
            aws_ses_access_key_id,
            aws_ses_secret_access_key
        )
        sender_ok = (sender_address in verified_addresses)
        if sender_ok:
            return True
        else:
            logging.warning(
                "Tried to send by AWS SES but %s is not verified." % (
            sender_address))
    return False


def send_email_by_service(to, subject, body, cc=None, bcc=None, html_body=None):
    " Send by AWS SES if available, otherwise GAE. "
    assert not isinstance(to, basestring), "'to' must be a list or iterable"

    # check for AWS API keys
    aws_ses_region = get_config_key('aws_ses_region')
    aws_ses_access_key_id = get_config_key('aws_ses_access_key_id')
    aws_ses_secret_access_key = get_config_key('aws_ses_secret_access_key')

    # lookup addresses(s) to send from
    gae_sender_address = get_appengine_default_system_email_address()
    aws_sender_address = get_aws_ses_default_system_email_address()

    # send by AWS or fall back to GAE
    # catch & log all exceptions to prevent blowing up requests due to email
    try:
        if can_send_by_aws_ses(aws_ses_region, aws_ses_access_key_id, aws_ses_secret_access_key, aws_sender_address):
            return send_email_via_aws_ses(
                aws_sender_address,
                to, subject, body, cc=cc, bcc=bcc, html_body=html_body,
                aws_ses_region=aws_ses_region,
                aws_ses_access_key_id=aws_ses_access_key_id,
                aws_ses_secret_access_key=aws_ses_secret_access_key
            )
        else:
            return send_email_via_appengine(
                gae_sender_address,
                to, subject, body, cc=cc, bcc=bcc, html_body=html_body
            )
    except:
        logging.exception("Exception caused generating email.")


def friendly_email_address(contact):
    return u"%s <%s>" % (contact.full_name, contact.email)


def email_contacts(event, contacts, subject, body, html=None, bcc_contacts=None):
    prefixed_subject = "[%s] %s" % (get_application_id(), subject)

    to_addresses = map(
        friendly_email_address,
        (contact for contact in contacts if contact.email)
    )
    bcc_addresses = map(
        friendly_email_address,
        (contact for contact in bcc_contacts if contact.email)
    ) if bcc_contacts else []

    send_email_by_service(
        to_addresses,
        prefixed_subject,
        body,
        bcc=bcc_addresses,
        html_body=html,
    )


def email_contacts_using_templates(
        event, contacts, subject_template_name, body_template_name, **kwargs):
    """
    Email contacts using Jinja2 templates.
    """
    subject_template = jinja_environment.get_template(subject_template_name)
    body_template = jinja_environment.get_template(body_template_name)

    kwargs.update({'event': event})

    rendered_subject = subject_template.render(kwargs)
    rendered_body = body_template.render(kwargs)

    email_contacts(event, contacts, rendered_subject, rendered_body)


def email_administrators(event, subject, body, html=None, include_local=True):
    admin_orgs = get_event_admins(event) if include_local else get_global_admins()
    admin_contacts = reduce(
        lambda x, y: list(x) + list(y),
        (org.contacts for org in admin_orgs)
    )
    email_contacts(event, admin_contacts, subject, body, html=html)


def email_administrators_using_templates(
    event, subject_template_name, body_template_name, include_local=True, **kwargs):
    """
    Email all relevant administrators for event, using Jinja2 templates.
    """
    admin_orgs = get_event_admins(event) if include_local else get_global_admins()
    admin_contacts = reduce(
        lambda x, y: list(x) + list(y),
        (org.contacts for org in admin_orgs)
    )
    email_contacts_using_templates(
        event,
        admin_contacts,
        subject_template_name,
        body_template_name,
        **kwargs
    )


#
# Specific email convenience functions
#

def send_activation_emails(org_for_activation):
    activation_url = "%s/activate?code=%s" % (
        get_base_url(), org_for_activation.activation_code)
    email_contacts_using_templates(
        None,
        org_for_activation.primary_contacts,
        'activation.subject.txt',
        'activation.body.txt',
        org=org_for_activation,
        activation_url=activation_url,
        bcc_contacts=get_global_admins()[0].contacts
    )


def send_activated_emails(org_activated):
    email_contacts_using_templates(
        org_activated.incidents[0],
        org_activated.primary_contacts,
        'activated.subject.txt',
        'activated.body.txt',
        org=org_activated,
        bcc_contacts=get_global_admins()[0].contacts
    )


#
# Test Handler
#


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
            send_email_by_service(
                sender=from_addr,
                to=[to_addr],
                subject=u"Test email",
                body=u"This is a test email."
            )
            self.response.out.write("Test email sent.")
        else:
            self.response.out.write("Need to and from addresses")
