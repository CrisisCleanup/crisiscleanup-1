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
import csv

# Local libraries.
import base
import site_db
import site_util

class ExportHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    self.AuthenticatedPost(org, event)

  def AuthenticatedPost(self, org, event):
    sites = site_util.SitesFromIds(self.request.get('id'), event)

    filename = 'work_sites.csv'
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = (
        'attachment; filename="work_sites.csv"')

    writer = csv.writer(self.response.out)
    writer.writerow(site_db.Site.CSV_FIELDS)

    for site in sites:
      writer.writerow(site.ToCsvLine())
