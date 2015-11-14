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
import jinja2
import os


# Local libraries.
import base
import page_db


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('admin_generate_new_password.html')

GLOBAL_ADMIN_NAME = "Admin"



class AdminGenerateNewPassword(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        global_admin = (org.name == GLOBAL_ADMIN_NAME)
        if not global_admin:
            self.redirect("/")
            return

        self.response.out.write(
            template.render(
                global_admin=global_admin
            )
        )
        
    def AuthenticatedPost(self, org, event):
        pass