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
# Basic utilities shared across the application.

# System libraries.
import cgi
import logging
import urllib
import webapp2

# For authentication

import key

class RequestHandler(webapp2.RequestHandler):
  """Base class for all of this app's request handlers.

  Currently just like webapp2.RequestHandler, except that it sends response
  headers to disable caching.
  """

  def __init__(self, *args, **kwargs):
    webapp2.RequestHandler.__init__(self, *args, **kwargs)
    self.disable_response_caching()

  def disable_response_caching(self):
    """Sets headers to disable response caching."""
    # Per http://stackoverflow.com/questions/49547/making-sure-a-web-page-is-not-cached-across-all-browsers.
    self.response.headers['Cache-Control'] = (
        'no-cache, no-store, must-revalidate')
    self.response.headers['Pragma'] = 'no-cache'
    self.response.headers['Expires'] = '0'

class AuthenticatedHandler(RequestHandler):
  def post(self):
    org, event = key.CheckAuthorization(self.request)
    if not org:
      self.HandleAuthenticationFailure('post')
      return
    for i in self.request.POST.keys():
      if hasattr(self.request.POST[i], 'replace'): # can be cgi-escaped?
        self.request.POST[i] = cgi.escape(self.request.POST[i])
    self.AuthenticatedPost(org, event)

  def get(self):
    org, event = key.CheckAuthorization(self.request)
    if not org:
      self.HandleAuthenticationFailure('get')
      return
    self.AuthenticatedGet(org, event)

  def put(self):
    org, event = key.CheckAuthorization(self.request)
    if not org:
      self.HandleAuthenticationFailure('put')
      return
    self.AuthenticatedPut(org, event)

  def HandleAuthenticationFailure(self, method):
    """Takes some action when authentication fails.
    This is its own method so that subclasses can customize the action.
    """
    if method == 'get':
      self.redirect("/home")
    else:
      # Redirecting to a non-GET URL doesn't really make sense.
      self.redirect("/authentication")
