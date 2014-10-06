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

# Local libraries.
import base
import site_db

PAGE_OFFSET = 1000


dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

open_statuses = [s for s in site_db.Site.status.choices if 'Open' in s]
closed_statuses = [s for s in site_db.Site.status.choices if not s in open_statuses]


class SiteAjaxHandler(base.AuthenticatedHandler):      

  DEFAULT_SITES_PER_PAGE = PAGE_OFFSET

  def AuthenticatedGet(self, org, event):
    # get params
    id_param = self.request.get('id')
    latitude_param = self.request.get("latitude")
    longitude_param = self.request.get("longitude")

    # set response to be json type for all cases
    self.response.headers['Content-Type'] = 'application/json'
    
    if latitude_param and longitude_param: # @@TODO this
      try:
        latitude = float(latitude_param)
        longitude = float(longitude_param)
      except:
        self.response.set_status(404)
      json_array = []
      for site in site_db.Site.gql(
           'Where latitude = :1 and longitude = :2 and event = :3', latitude, longitude, event.key()):
        json_string = json.dumps({
            "id": site.key().id(),
            "address": site.address,
        })
        json_array.append(json_string)
      self.response.out.write(
            json.dumps(json_array, default = dthandler))      
      return

    if id_param == 'all':
        status_param = self.request.get("status", default_value="")
        short_status = {
            'open': site_db.SHORT_STATUS_OPEN,
            'closed': site_db.SHORT_STATUS_CLOSED
        }.get(status_param, None)
        page_param = self.request.get("page", default_value="0")
        page = int(page_param)

        site_pins = site_db.Site.pins_in_event(
            event.key(),
            self.DEFAULT_SITES_PER_PAGE,
            page,
            short_status=short_status
        )
        json_output = json.dumps(
            site_pins,
            default=dthandler
        )
        raise Exception(json_output)
        self.response.out.write(json_output)
        return
      
    try:
      id = int(id_param)
    except:
      self.response.set_status(404)
      return
    site = site_db.GetAndCache(id)
    if not site:
      self.response.set_status(404)
      return
    # TODO(jeremy): Add the various fixes for Flash
    # and other vulnerabilities caused by having user-generated
    # content in JSON strings, by setting this as an attachment
    # and prepending the proper garbage strings.
    # Javascript security is really a pain.
    self.response.out.write(
        json.dumps(
            site.as_dict,
            default=dthandler
        )
    )