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
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db
import event_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteHandler(base.AuthenticatedHandler):
  """Handler to confirm and then actually delete a site."""
  def AuthenticatedGet(self, org, event):
    try:
      id = int(self.request.get('id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site_db.SiteForm(self.request.POST, site),
                       "id": id,
                       "delete": True}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def AuthenticatedPost(self, org, event):
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    if site:
      site.delete()
      event_id = event.key().id()
    self.redirect('/sites?message=Site Deleted')
