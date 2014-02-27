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
# System libraries.
from time import sleep

# Local libraries.
from admin_base import AdminAuthenticatedHandler

from config_key_db import ConfigKey


class AdminGlobalSettingsHandler(AdminAuthenticatedHandler):

    template = "admin_global_settings.html"

    accessible_to_local_admin = False

    def AuthenticatedGet(self, org, event):
        config_keys = ConfigKey.all().order('name')
        return self.render(
            config_keys=config_keys
        )

    def AuthenticatedPost(self, org, event):
        config_keys = ConfigKey.all()
        keys_by_name = {cf.name:cf for cf in config_keys}
        for k, v in self.request.POST.items():
            config_key = keys_by_name.get(k)
            if config_key:
                config_key.value = v
                config_key.save()

        # sleep to wait for db
        sleep(3)

        # redirect to self
        return self.redirect(self.request.path)
