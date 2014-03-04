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

import json

import base


class HomeHandler(base.FrontEndAuthenticatedHandler):

    template_filename = 'home.html'

    def get(self):
        try:
            with open('version.json') as version_json_fd:
                version_d = json.load(version_json_fd)
        except:
            version_d = None

        self.render(
            version_d=version_d,
        )
