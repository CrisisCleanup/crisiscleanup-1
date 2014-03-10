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
import datetime
import json
import os

# Local libraries.
import base
import key
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None


class MapHandler(base.FrontEndAuthenticatedHandler):

  template_filenames = ['main.html', '_menubox.html']

  def get(self):
    filters = [
              #["debris_only", "Remove Debris Only"],
              #["electricity", "Has Electricity"],
              #["no_standing_water", "No Standing Water"],
              #["not_habitable", "Home is not habitable"],
              #["Flood", "Primary problem is flood damage"],
              #["Trees", "Primary problem is trees"],
              #["Goods or Services", "Primary need is goods and services"]]
              #["CT", "Connecticut"],
              #["NJ", "New Jersey"],
              #["NY", "New York"]]
              ["Health", "Health"],
              ["Food", "Food"]]

    org, event = key.CheckAuthorization(self.request)

    if org.permissions == "Situational Awareness":
      return self.redirect("/sit_aware_redirect")

    if org:
      filters = [#["claimed", "Claimed by " + org.name],
                 #["unclaimed", "Unclaimed"],
                 ["open", "Open"],
                 #["closed", "Closed"],
                 ["reported", "Reported by " + org.name],
                 ] + filters

      site_id = self.request.get("id")
      # default to 15
      zoom_level = self.request.get("z", default_value = "15")

      menubox_content = self.get_template('_menubox.html').render(
        org=org,
        event=event,
        include_search=True,
        admin=org.is_admin
      )
      return self.render(
          template='main.html',
          version=os.environ['CURRENT_VERSION_ID'],
          counties=event.counties,
          org=org,
          menubox=menubox_content,
          status_choices=[
            json.dumps(c) for c in site_db.Site.status.choices
          ],
          filters=filters,
          demo=False,
          zoom_level=zoom_level,
          site_id=site_id,
	  event_name=event.name,
      )
    else:
        self.abort(403)
