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
from google.appengine.ext import db

import cache

class Organization(db.Model):
  # Data about the organization.
  name = db.StringProperty(required = True)
  # We store passwords in plain text, because we want to
  # set the passwords ourselves, and may need to be able
  # to retrieve them for an organization.
  password = db.StringProperty(required = True)
  primary_contact_email = db.StringProperty(default = '')
  # If set, then only session cookies are sent to the
  # user's browser. Otherwise, they'll receive cookies that
  # will expire in 1 week.
  only_session_authentication = db.BooleanProperty(default = True)

ten_minutes = 600
def GetCached(org_id):
  return cache.GetCachedById(Organization, ten_minutes, org_id)

def GetAndCache(org_id):
  return cache.GetAndCache(Organization, ten_minutes, org_id)

def GetAllCached():
  return cache.GetAllCachedBy(Organization, ten_minutes)
