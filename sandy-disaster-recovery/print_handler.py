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
import math

# Local libraries.
import base
import site_util

# Only works for EST!
LOCAL_TIME_OFFSET = datetime.timedelta(seconds=-5 * 3600)
HATTIESBURG_SHORT_NAME = "hattiesburg"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"
MOORE_OKLAHOMA_SHORT_NAME = "moore"


def silent_none(value):
  if value is None:
    return ''
  return value


class PrintHandler(base.FrontEndAuthenticatedHandler):

  template_filenames = [
    'print.html',
    'print_single.html',
    'print_single_derechos.html',
    'print_single_moore.html',
  ]

  def __init__(self, *args, **kwargs):
      super(PrintHandler, self).__init__(*args, **kwargs)
      self.jinja_environment.finalize = silent_none

  def AuthenticatedGet(self, org, event):
    self.AuthenticatedPost(org, event)

  def AuthenticatedPost(self, org, event):
    template_filename = {
        HATTIESBURG_SHORT_NAME: 'print_single_derechos.html',
        GEORGIA_SHORT_NAME: 'print_single_derechos.html',
        MOORE_OKLAHOMA_SHORT_NAME: 'print_single_moore.html',
    }.get(event.short_name, 'print_single.html')
    print_single_template = self.get_template(template_filename)
        
    sites = site_util.SitesFromIds(self.request.get('id'), event)

    return self.render(
        template='print.html',
        content=''.join(print_single_template.render({
            'page_break': i > 0,
            'show_map': math.fabs(site.latitude) > 0,
            'id': site.key().id(),
            'site': site,
            'readonly': True,
            'current_local_time': datetime.datetime.utcnow() + LOCAL_TIME_OFFSET,
            'request_local_time': site.request_date + LOCAL_TIME_OFFSET
        }) for i, site in enumerate(sites))
    )
