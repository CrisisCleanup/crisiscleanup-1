#!/usr/bin/env python
#
# Copyright 2014 Chris Wood
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
from event_db import Event
from config_key_db import get_config_key


jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('about.html')


class CatchAllHandler(base.RequestHandler):

    def get(self, path):
        # path is assumed to be an incident short name -- check
        event = Event.all().filter('short_name', path).get()
        if not event:
            self.abort(404)

        # switch on config option
        config_setting = get_config_key('handle_incident_short_names')
        if config_setting == 'public_map':
            self.redirect('/public-map?initial_incident_id=' + event.short_name)
            return
        elif config_setting == 'authentication':
            self.redirect('/authentication?initial_event_name=' + event.name)
            return
        else:
            self.abort(404)
