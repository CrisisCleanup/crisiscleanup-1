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
import cgi
import json
import logging
from google.appengine.ext import db

# Local libraries.
import base
import site_db

# HTTP status codes.
BAD_REQUEST = 400
FORBIDDEN = 403

class SiteApiHandler(base.AuthenticatedHandler):
  def AuthenticatedPut(self, org, event):
    """Handles updating site fields."""
    # raw_data = '{"id": 1, "update": {"status": "Open, unassigned"}}'
    json_request = json.loads(cgi.escape(self.request.body))

    REQUIRED_KEYS = ['id', 'action']
    if not self.CheckRequiredKeys(json_request, REQUIRED_KEYS):
      return

    if json_request['action'] == 'update':
      self.HandleUpdate(json_request)
    elif json_request['action'] == 'claim':
      self.HandleClaim(json_request, org)
    elif json_request['action'] == 'release':
      self.HandleRelease(json_request, org)
    else:
      self.HandleBadRequest('invalid action: %s' % json_request['action'])

  def HandleUpdate(self, json_request):
    if not self.CheckRequiredKeys(json_request, ['update']):
      return

    VALIDATORS = {
        'status': lambda field, status: status in site_db.Site.status.choices,
        }

    unsupported_fields = [f for f in json_request['update']
                          if f not in VALIDATORS]
    if unsupported_fields:
      self.HandleBadRequest('cannot update these fields: %s' %
                            ', '.join(unsupported_fields))
      return

    invalid_fields = []
    for field, value in json_request['update'].iteritems():
      validator = VALIDATORS[field]
      if not validator(field, value):
        invalid_fields.append(field)

    if invalid_fields:
      self.HandleBadRequest('invalid values for these fields: %s' %
                            ', '.join(invalid_fields))
      return

    site = self.GetSite(json_request['id'])
    if not site:
      return

    for field, value in json_request['update'].iteritems():
      setattr(site, field, value)
    site_db.PutAndCache(site)
    logging.debug('updated site')

  def HandleRelease(self, json_request, org):
    """Releases a site for an organization, if it was claimed by the organization."""
    site = self.GetSite(json_request['id'])
    if not site:
      return

    claimed_by = None
    try:
      claimed_by = site.claimed_by
    except db.ReferencePropertyResolveError:
      # Treat the site as if it has no organization.
      logging.warning('failed to find organization for site %s' %
                      json_request['id'])
      pass
    if claimed_by and claimed_by.key().id() == org.key().id():
      site.claimed_by = None
      site_db.PutAndCache(site)
      return

    if claimed_by:
      self.HandleBadRequest(
          'This site is claimed by ' + claimed_by.name + '.',
          status=FORBIDDEN)
    else:
      self.HandleBadRequest('This site is currently unclaimed.',
                            status=FORBIDDEN)

  def HandleClaim(self, json_request, org):
    """Claims a site for an organization, if it's not already taken."""
    site = self.GetSite(json_request['id'])
    if not site:
      return

    claimed_by = None
    try:
      claimed_by = site.claimed_by
    except db.ReferencePropertyResolveError:
      # Treat the site as if it has no organization.
      logging.warning('failed to find organization for site %s' %
                      json_request['id'])
      pass

    if not claimed_by:
      site.claimed_by = org
      site_db.PutAndCache(site)
      return

    if site.claimed_by.key().id() == org.key().id():
      self.response.out.write(
          'This site was already claimed by your organization.')
    else:
      self.HandleBadRequest('Sorry, this site has already been claimed by %s' %
                            site.claimed_by.name, status=FORBIDDEN)

  def CheckRequiredKeys(self, json_request, required_keys):
    """Ensures that json_request contains the given keys.
    If it does, returns True.
    Otherwise, marks the request as bad and returns False.
    """
    missing_keys = [k for k in required_keys if k not in json_request]
    if missing_keys:
      self.HandleBadRequest('missing these required keys: %s' %
                            ', '.join(missing_keys))
      return False
    return True

  def GetSite(self, id):
    site = site_db.Site.get_by_id(id)
    if not site:
      self.HandleBadRequest('no site with id %s' % id)
      return None
    return site

  def HandleBadRequest(self, message, status=BAD_REQUEST):
    logging.warning('Bad JSON request: %s' % message)
    self.response.set_status(status)  # Bad request.
    self.response.out.write(message)

  def HandleAuthenticationFailure(self, method):
    if method == 'get':
      return base.AuthenticatedHandler.HandleAuthenticationFailure(self, method)
    self.response.set_status(401)  # Unauthorized.
