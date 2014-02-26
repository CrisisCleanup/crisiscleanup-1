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
import functools
import codecs
from collections import namedtuple

from google.appengine.ext import db
from google.appengine.api import app_identity, mail

import jinja2

from config_key_db import get_config_key

from admin_handler.admin_identity import get_global_admins, get_local_admins, get_event_admins

import aws


# jinja

DEFAULT_TEMPLATES_PATH = os.path.join(
    os.path.dirname(__file__),
    'templates', 'email', 'defaults'
)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'templates',
            'email'
        )
    )
)


#
# define all emails sent by the system inc. the names of their templates
#

EmailDescription = namedtuple(
    'EmailDescription', [
    'name',
    'friendly_name',
    'description',
    'variables',  # so-named in Jinja2
])

EMAIL_DESCRIPTIONS = [

    EmailDescription(
        u'new_organization.to_organization',
        u'New organization email for orgs',
        u'Sent to primary contacts of an org when they sign up.',
        u'org, new_contacts, application_id'
    ),

    EmailDescription(
        u'new_organization.to_admins',
        u'New organization email for admins',
        u'Sent to admins when an org signs up.',
        u'org, new_contacts, application_id, approval_url'
    ),

    EmailDescription(
        u'activation',
        u'Activation Email',
        u'Sent to the primary contacts of an org when verified.',
        u'org, activation_url'
    ),

    EmailDescription(
        u'activated',
        u'Activated Email',
        u'Sent to the primary contacts of a newly activated org.',
        u'org'
    ),

    EmailDescription(
        u'organization_joins_incident.to_admins',
        u'Organization joins incident for admins',
        u'Sent to admins when an org joins a new incident.',
        u'org, review_url'
    )
]

EMAIL_DESCRIPTIONS_BY_NAME = {ed.name: ed for ed in EMAIL_DESCRIPTIONS}


#
# admin-editable email template entities
#

class EmailTemplate(db.Model):

    name = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    html_body = db.TextProperty()
    use_html = db.BooleanProperty(default=False)
    bcc_local_admins = db.BooleanProperty(default=False)
    bcc_global_admins = db.BooleanProperty(default=False)

    @classmethod
    def get_by_name(cls, name):
        " Get or create, using defaults. "
        if name not in EMAIL_DESCRIPTIONS_BY_NAME:
            raise Exception("Unknown email: '%s'" % name)
        existing = cls.all().filter('name', name).get()
        if existing:
            return existing
        else:
            # create new from defaults
            default_subject_fd = codecs.open(
                os.path.join(DEFAULT_TEMPLATES_PATH, '%s.subject.txt' % name),
                encoding='utf-8'
            )
            default_body_fd = codecs.open(
                os.path.join(DEFAULT_TEMPLATES_PATH, '%s.body.txt' % name),
                encoding='utf-8'
            )
            new_email_template = EmailTemplate(
                name=name,
                subject=default_subject_fd.read().strip(),
                body=default_body_fd.read().strip(),
            )
            new_email_template.save()
            return new_email_template


#
# helper functions
#

def get_application_id():
    return app_identity.get_application_id()


def get_default_version_hostname():
    return app_identity.get_default_version_hostname()


def get_base_url():
    " Returns http as the scheme - assumes requests will be redirected. "
    return "http://" + get_default_version_hostname()


def get_app_system_email_address():
    system_email_address = get_config_key('system_email_address')
    if system_email_address:
        return system_email_address
    else:
        return "%s <noreply@%s.appspotmail.com>" % (
            app_identity.get_service_account_name(),
            app_identity.get_application_id()
        )

def friendly_email_address(contact):
    return u"%s <%s>" % (contact.full_name, contact.email)


#
# email transport functions
#

def send_email_via_appengine(
        sender, to, subject, body, cc=None, bcc=None, html_body=None
    ):
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


def send_email_by_service(
        sender, to, subject, body, cc=None, bcc=None, html_body=None
    ):
    " Send by AWS SES if available, otherwise GAE. "
    # check for AWS API keys
    aws_ses_region = get_config_key('aws_ses_region')
    aws_ses_access_key_id = get_config_key('aws_ses_access_key_id')
    aws_ses_secret_access_key = get_config_key('aws_ses_secret_access_key')

    if aws_ses_region and aws_ses_access_key_id and aws_ses_secret_access_key:
        return send_email_via_aws_ses(
            sender, to, subject, body, cc=cc, bcc=bcc, html_body=html_body,
            aws_ses_region=aws_ses_region,
            aws_ses_access_key_id=aws_ses_access_key_id,
            aws_ses_secret_access_key=aws_ses_secret_access_key
        )
    else:
        return send_email_via_appengine(
            sender, to, subject, body, cc=cc, bcc=bcc, html_body=html_body
        )


#
# email to contacts functions
# (not to be used directly)
#


def email_contacts(event, contacts, subject, body, html=None, bcc_contacts=None):
    prefixed_subject = "[%s] %s" % (get_application_id(), subject)
    sender_address = get_app_system_email_address()

    to_addresses = map(
        friendly_email_address,
        (contact for contact in contacts if contact.email)
    )
    bcc_addresses = map(
        friendly_email_address,
        (contact for contact in bcc_contacts if contact.email)
    ) if bcc_contacts else []

    send_email_by_service(
        sender_address,
        to_addresses,
        prefixed_subject,
        body,
        bcc=bcc_addresses,
        html_body=html,
    )


def email_contacts_using_templates(event, contacts, email_name, **kwargs):
    """
    Email contacts using Jinja2 templates.
    """
    # lookup templates
    email_template_entity = EmailTemplate.get_by_name(email_name)
    subject_template = jinja2.Template(email_template_entity.subject)
    body_template = jinja2.Template(email_template_entity.body)
    html_body_template = (
        jinja2.Template(email_template_entity.html_body) 
        if email_template_entity.use_html
        else None
    )

    # render templates
    kwargs.update({'event': event})
    rendered_subject = subject_template.render(kwargs)
    rendered_body = body_template.render(kwargs)
    rendered_html = html_body_template.render(kwargs) if html_body_template else None

    # decide additional bccs
    bcc_contacts = []
    if email_template_entity.bcc_global_admins:
        for global_admin in get_global_admins():
            bcc_contacts.extend(global_admin.contacts)
    if email_template_entity.bcc_local_admins:
        for local_admin in get_local_admins(event):
            bcc_contacts.extend(local_admin.contacts)

    # send rendered emails to contacts
    email_contacts(
        event,
        contacts,
        rendered_subject,
        rendered_body,
        html=rendered_html,
        bcc_contacts=bcc_contacts
    )


def email_administrators(event, subject, body, html=None, include_local=True):
    admin_orgs = get_event_admins(event) if include_local else get_global_admins()
    admin_contacts = reduce(lambda x, y: x+y, (org.contacts for org in admin_orgs))
    email_contacts(event, admin_contacts, subject, body, html=html)


def email_administrators_using_templates(event, email_name, include_local=True, **kwargs):
    """
    Email all relevant administrators for event, using Jinja2 templates.
    """
    admin_orgs = get_event_admins(event) if include_local else get_global_admins()
    admin_contacts = reduce(lambda x, y: x+y, (list(org.contacts) for org in admin_orgs))
    email_contacts_using_templates(
        event,
        admin_contacts,
        email_name,
        **kwargs
    )


#
# Specific email methods
#
# (all prevented from raising exceptions to avoid blowing up the caller)
#

def catch_exceptions(exception=Exception, logger=logging.getLogger(__name__)):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except exception as err:
                logging.error(u"Exception occured. Traceback follows.")
                logger.exception(err)
            else:
                return result
        return wrapper
    return deco


@catch_exceptions()
def send_new_organization_email_to_organization(event, org, contacts):
    primary_contacts = [c for c in contacts if c.is_primary]
    email_contacts_using_templates(
        event,
        primary_contacts,
        'new_organization.to_organization',
        org=org,
        new_contacts=contacts,
        application_id=get_application_id(),
    )


@catch_exceptions()
def send_new_organization_email_to_admins(event, org, contacts, approval_url):
    email_administrators_using_templates(
        event,
        'new_organization.to_admins',
        org=org,
        new_contacts=contacts,
        application_id=get_application_id(),
        approval_url=approval_url,
    )

@catch_exceptions()
def send_organization_joins_incident_email_to_admins(event, org, review_url):
    email_administrators_using_templates(
        event,
        'organization_joins_incident.to_admins',
        org=org,
        review_url=review_url,
    )


@catch_exceptions()
def send_activation_emails(org_for_activation):
    activation_url = "%s/activate?code=%s" % (
        get_base_url(),
        org_for_activation.activation_code
    )
    email_contacts_using_templates(
        None,
        org_for_activation.primary_contacts,
        'activation',
        org=org_for_activation,
        activation_url=activation_url,
    )


@catch_exceptions()
def send_activated_emails(org_activated):
    email_contacts_using_templates(
        None,
        org_activated.primary_contacts,
        'activated',
        org=org_activated,
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
