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

import base
from primary_contact_db import Contact, ContactFormFull


class ContactInfoHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'contact_info.html'

    def AuthenticatedGet(self, org, event):
        try:
            contact_id = int(self.request.get("contact", -1))
            contact = Contact.get_by_id(contact_id)
        except:
            self.abort(404)
        if not contact:
            self.abort(404)

        return self.render(
            contact=contact,
            form=ContactFormFull(None, contact)  # used to iterate over fields
        )
