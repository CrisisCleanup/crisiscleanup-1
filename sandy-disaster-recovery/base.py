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
import os
import cgi

import webapp2
import jinja2

# enable GAE ereporter
from google.appengine.ext import ereporter
ereporter.register_logger()

from config_key_db import get_config_key
from page_db import get_page_block_dict


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

  def AuthenticatedGet(self, *args, **kwargs):
      # unless implemented, method is not allowed
      self.abort(405)

  def AuthenticatedPost(self, *args, **kwargs):
      # unless implemented, method is not allowed
      self.abort(405)

  def AuthenticatedPut(self, *args, **kwargs):
      # unless implemented, method is not allowed
      self.abort(405)

  def HandleAuthenticationFailure(self, method):
    """Takes some action when authentication fails.
    This is its own method so that subclasses can customize the action.
    """
    if method == 'get':
      self.redirect("/home")
    else:
      # Redirecting to a non-GET URL doesn't really make sense.
      self.redirect("/authentication")


def get_template_path():
    # lookup template set to use
    template_set_name = get_config_key('template_set') or 'default'

    # construct path
    return os.path.join(
        os.path.dirname(__file__),
        'templates',
        'html',
        template_set_name
    )


def get_template_environment():
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            get_template_path()
        )
    )


class FrontEndAuthenticatedHandler(AuthenticatedHandler):

    # template(s) to use
    template_filename = None
    template_filenames = None

    use_page_blocks = True

    def __init__(self, *args, **kwargs):
        super(AuthenticatedHandler, self).__init__(*args, **kwargs)

        # store a jinja env
        self.jinja_environment = get_template_environment()

        # load templates by filename
        filenames = (
            ([self.template_filename] if self.template_filename else []) +
            (self.template_filenames or [])
        )
        if filenames:
            self._templates = {} 
            for filename in filenames:
                self._templates[filename] = self.jinja_environment.get_template(filename) 
        else:
            raise Exception("No template filenames defined.")

    def dispatch(self, *args, **kwargs):
        # check auth
        org, event = key.CheckAuthorization(self.request)
        logged_in = bool(org and event)
        self.request.logged_in = logged_in

        try:
            self.pre_dispatch()
        except:
            return # bail

        # dispatch
        super(FrontEndAuthenticatedHandler, self).dispatch(*args, **kwargs)

        self.post_dispatch()

    def pre_dispatch(self):
        pass

    def post_dispatch(self):
        pass

    def get_template(self, filename):
        return self._templates[filename]

    def render(self, **kwargs):
        """
        Render jinja template to response out.

        Template can be selected py passing template kwarg.

        Passed to every template:
        * page blocks (micro-CMS)
        * logged_in bool
        """
        # select template
        if kwargs.get('template'):
            template = self._templates[kwargs.get('template')]
        elif len(self._templates) == 1:
            template = self._templates.values()[0]
        else:
            raise Exception("Must select a template to render.")

        # get page blocks
        page_block_params = get_page_block_dict()
        return self.response.out.write(
            template.render(
                dict(
                    page_block_params,
                    logged_in=self.request.logged_in,
                    **kwargs)
            )
        )


class PublicAuthenticatedHandler(FrontEndAuthenticatedHandler):


    " Overide get for simple public-facing pages. "

    def get(self):
        " Convenient default for simple pages. "
        self.render()
