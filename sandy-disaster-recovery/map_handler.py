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

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('main.html')
logout_template = jinja_environment.get_template('logout.html')
class MapHandler(base.RequestHandler):
  def get(self):
    filters = [
              ["debris_only", "Remove Debris Only"],
              ["electricity", "Has Electricity"],
              ["no_standing_water", "No Standing Water"],
              ["not_habitable", "Home is not habitable"],
              ["Flood", "Primary problem is flood damage"],
              ["Trees", "Primary problem is trees"],
              ["Goods or Services", "Primary need is goods and services"],
              ["CT", "Connecticut"],
              ["NJ", "New Jersey"],
              ["NY", "New York"]]

    org, event = key.CheckAuthorization(self.request)
    if org:
      filters = [["claimed", "Claimed by " + org.name],
                 ["unclaimed", "Unclaimed"],
                 ["open", "Open"],
                 ["closed", "Closed"],
                 ["reported", "Reported by " + org.name],
                 ] + filters

      site_id = self.request.get("id")
      # default to 15
      zoom_level = self.request.get("z", default_value = "15")

      template_values = {
          "version" : os.environ['CURRENT_VERSION_ID'],
          #"uncompiled" : True,
          "counties" : event.counties,
          "org" : org,
          "logout" : logout_template.render({"org": org,
                                             "event": event,
                                             "include_search": True}),
          "status_choices" : [json.dumps(c) for c in
                              site_db.Site.status.choices],
          "filters" : filters,
          "demo" : False,
          "zoom_level" : zoom_level,
          "site_id" :  site_id
        }
    else:
      # TODO(Jeremy): Temporary code until this handler scales.
      self.redirect("/authentication?destination=/map")
      return
      # Allow people to bookmark an unauthenticated event map,
      # by setting the event ID.
      event = event_db.GetEventFromParam(self.request.get("event_id"))
      if not event:
        self.response.set_status(404)
        return
      template_values = {
          "sites" :
             [json.dumps({
                 "latitude": round(s.latitude, 2),
                 "longitude": round(s.longitude, 2),
                 "debris_removal_only": s.debris_removal_only,
                 "electricity": s.electricity,
                 "standing_water": s.standing_water,
                 "tree_damage": s.tree_damage,
                 "habitable": s.habitable,
                 "electrical_lines": s.electrical_lines,
                 "cable_lines": s.cable_lines,
                 "cutting_cause_harm": s.cutting_cause_harm,
                 "work_type": s.work_type,
                 "state": s.state,
                 }) for s in [p[0] for p in site_db.GetAllCached(event)]],
          "filters" : filters,
          "demo" : True,
        }
    self.response.out.write(template.render(template_values))
