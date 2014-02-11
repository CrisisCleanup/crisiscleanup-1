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
import jinja2
import json
import os
from google.appengine.ext import db
from google.appengine.api import memcache

# Local libraries.
import base
import event_db
import key
import site_db
import page_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('main.html')
menubox_template = jinja_environment.get_template('_menubox.html')


class MapHandler(base.RequestHandler):

  DEFAULT_ZOOM_LEVEL = 15

  def get(self):
    filters = [
              #["debris_only", "Remove Debris Only"],
              #["electricity", "Has Electricity"],
              #["no_standing_water", "No Standing Water"],
              #["not_habitable", "Home is not habitable"],
              ["Flood", "Primary problem is flood damage"],
              ["Trees", "Primary problem is trees"],
              ["Goods or Services", "Primary need is goods and services"]]
              #["CT", "Connecticut"],
              #["NJ", "New Jersey"],
              #["NY", "New York"]]

    # check org authed
    org, event = key.CheckAuthorization(self.request)
    if not org:
      # bail out
      self.redirect("/authentication?destination=/map")
      return

    # render template
    filters = [["claimed", "Claimed by " + org.name],
               ["unclaimed", "Unclaimed"],
               ["open", "Open"],
               ["closed", "Closed"],
               ["reported", "Reported by " + org.name],
               ] + filters
    site_id = self.request.get("id")
    zoom_level = self.request.get("z", default_value=str(self.DEFAULT_ZOOM_LEVEL))
    template_values = page_db.get_page_block_dict()
    template_values.update({
        "version" : os.environ['CURRENT_VERSION_ID'],
        #"uncompiled" : True,
        "counties" : event.counties,
        "org" : org,
        "menubox" : menubox_template.render({"org": org,
                                           "event": event,
                                           "include_search": True,
                                           "admin": org.is_admin,
                                           }),
        "status_choices" : [json.dumps(c) for c in
                            site_db.Site.status.choices],
        "filters" : filters,
        "demo" : False,
        "zoom_level" : zoom_level,
        "site_id" :  site_id,
        "event_name": event.name,
    })
    self.response.out.write(template.render(template_values))
