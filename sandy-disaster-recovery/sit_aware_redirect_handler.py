#!/usr/bin/env python
#
# Copyright 2014 Andy Gimma
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
import cgi
import jinja2
import os
import urllib2
import wtforms.validators
from google.appengine.ext import db
import json
from datetime import datetime



# Local libraries.
import base
import event_db
import site_db
import form_db
import page_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

template = jinja_environment.get_template('permissions_redirect_page.html')

class SitAwareRedirectHandler(base.AuthenticatedHandler):

  def AuthenticatedGet(self, org, event):
      self.response.out.write(template.render({}))

