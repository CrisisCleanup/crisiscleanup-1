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

from google.appengine.api import app_identity, mail


ADMINISTRATORS = [
    ('Aaron Titus', 'aaron@crisiscleanup.org')
]


def get_app_system_email_address():
    return "%s <noreply@%s.appspotmail.com>" % (
        app_identity.get_service_account_name(),
        app_identity.get_application_id()
    )

def email_administrators(subject, body):
    """
    Email all ADMINISTRATORS with an email of @body and rewritten
    @subject of "[myappid] <@subject>"
    """
    subject = "[%s] %s" % (app_identity.get_application_id(), subject)
    sender_address = get_app_system_email_address()
    for name, email_address in ADMINISTRATORS:
        recipient_address = "%s <%s>" % (name, email_address)
        mail.send_mail(
            sender_address,
            recipient_address,
            subject,
            body
        )
