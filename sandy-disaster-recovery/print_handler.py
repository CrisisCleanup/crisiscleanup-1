#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
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
import logging
import math
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_util

def silent_none(value):
     if value is None:
         return ''
     return value

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.finalize = silent_none
template = jinja_environment.get_template('print.html')
single_site_template = jinja_environment.get_template('single_site.html')
print_single_template = jinja_environment.get_template('print_single.html')

class PrintHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    self.AuthenticatedPost(org, event)

  def AuthenticatedPost(self, org, event):
    sites = site_util.SitesFromIds(self.request.get('id'), event)
    content_chunks = []
    first_time = True
    for site in sites:
      template_values = {"form": site,
                         "id": site.key().id(),
                         "readonly": True}
      content_chunks.append(print_single_template.render({
          "page_break": not first_time,
          "show_map": math.fabs(site.latitude) > 0,
          "id": site.key().id(),
          "form": site,
          "single_site": single_site_template.render(template_values),
          }))
      first_time = False
    self.response.out.write(template.render({
        "content": ''.join(content_chunks)
        }))
