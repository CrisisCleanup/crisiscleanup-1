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
# System libraries
from google.appengine.ext.db import Query
# Local libraries.
import site_db

# TODO(Jeremy): Deprecate this once we move to server-side
# filter generation.
def SitesFromIds(comma_separated_ids, event):
  """Given a string of ids, like "1,2,3", returns corresponding Site objects.
  If comma_separated_ids is empty, returns all sites.
  """
  if not comma_separated_ids:
    return [site[0] for site in site_db.GetAllCached(event)]
  else:
    try:
      ids = [int(id) for id in comma_separated_ids.split(',')]
    except:
      return None
    return [site[0] for site in site_db.GetAllCached(event, ids = ids)]


#  copied from http://wiki.python.org/moin/EscapingHtml
def unescape(s):
  s = s.replace("&lt;", "<")
  s = s.replace("&gt;", ">")
  # this has to be last:
  s = s.replace("&amp;", "&")
  return s