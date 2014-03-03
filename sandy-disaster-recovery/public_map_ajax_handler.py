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

from more_itertools import first

# Local libraries
import base
import site_db
import event_db

PAGE_OFFSET = 1000

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None


class PublicMapAjaxHandler(base.RequestHandler):      

  def get(self):
    # get params
    event_shortname = self.request.get("shortname")
    page = self.request.get("page")
    page_int = int(page)

    # select event
    if event_shortname == None:
      event_shortname = "sandy"
    events = event_db.GetAllCached()
    event = first(
        (event for event in events if event.short_name == event_shortname),
        None
    )
    if not event:
        self.abort(404)

    # get public pins (as dicts)
    site_dicts = site_db.Site.public_pins_in_event(
        event.key(),
        PAGE_OFFSET,
        page_int,
        short_status=site_db.SHORT_STATUS_OPEN
    )
	
    # return as json
    output = json.dumps(
        site_dicts,
	default=dthandler
    )
    self.response.out.write(output)
