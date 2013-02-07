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
import webapp2
from webapp2_extras import routes

# Local libraries.
import authentication_handler
import base
import delete_handler
import edit_handler
import export_handler
import form_handler
import import_handler
import key
import map_handler
import print_handler 
import problem_handler
import refresh_handler
import site_ajax_handler
import site_api_handler
import sites_handler
import new_organization_handler
import new_incident_handler
import admin_handler
import update_handler
import update_event_handler
import welcome_handler
import organization_ajax_handler

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

MAP_URL = "http://maps.google.com/?q=http://www.aarontitus.net/maps/sandy_work_orders.kmz"
SPREADSHEET_URL = "https://docs.google.com/spreadsheet/ccc?key=0AhBdPrWyrhIfdFVHMDFOc0NCQjNNbmVvNHJybTlBUXc#gid=0"

class LogoutHandler(base.RequestHandler):
  def get(self):
    self.response.headers.add_header("Set-Cookie",
                                     key.GetDeleteCookie())
    self.redirect("/authentication")

class Route(routes.RedirectRoute):
  def __init__(self, *args, **kwargs):
    # This causes a URL to redirect to its canonical version without a slash.
    # See http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
    if 'strict_slash' not in kwargs:
      kwargs['strict_slash'] = True
    routes.RedirectRoute.__init__(self, *args, **kwargs)

app = webapp2.WSGIApplication([
    Route(r'/refresh_counties', refresh_handler.RefreshHandler, name='refresh_counties'),
    Route(r'/old', redirect_to=SPREADSHEET_URL, name='spreadsheet_redirect'),
    Route(r'/api/site', site_api_handler.SiteApiHandler, 'site_api'),
    Route(r'/api/site_ajax', site_ajax_handler.SiteAjaxHandler, 'site_ajax'),
    Route(r'/authentication', authentication_handler.AuthenticationHandler,
          'auth'),
    Route(r'/export', export_handler.ExportHandler, 'export'),
    Route(r'/logout', LogoutHandler, 'logout'),
    Route(r'/delete', delete_handler.DeleteHandler, 'delete'),
    Route(r'/dev', form_handler.FormHandler, 'dev'),
    Route(r'/', form_handler.FormHandler, 'dev'),
    Route(r'/dev/map', map_handler.MapHandler, 'map'),
    Route(r'/dev/maps', redirect_to_name='map', name='maps_redirect'),
    Route(r'/map', map_handler.MapHandler, 'map'),
    Route(r'/maps', redirect_to_name='map', name='maps_redirect'),
    Route(r'/edit', edit_handler.EditHandler, 'edit'),
    Route(r'/import', import_handler.ImportHandler, 'import'),
    Route(r'/old/map', redirect_to=MAP_URL, name='external_map_redirect'),
    Route(r'/old/maps', redirect_to_name=MAP_URL, name='external_maps_redirect'),
    Route(r'/print', print_handler.PrintHandler, 'print'),
    Route(r'/problems', problem_handler.ProblemHandler, 'problems'),
    Route(r'/sites', sites_handler.SitesHandler, 'sites'),
    Route(r'/new_organization', new_organization_handler.NewOrganizationHandler, 'new_organization'),
    #Route(r'/new_incident', new_incident_handler.NewIncidentHandler, 'new_incident'),
    Route(r'/admin', admin_handler.AdminHandler, 'admin_handler'),
    Route(r'/update_handler', update_handler.UpdateHandler, 'update_handler'),
    Route(r'/update_event_handler', update_event_handler.UpdateHandler, 'update_event_handler'),
    Route(r'/welcome', welcome_handler.WelcomeHandler, 'welcome_handler'),
    Route(r'/organization_ajax_handler', organization_ajax_handler.OrganizationAjaxHandler, 'organization_ajax_handler'),
    
    
    
    
    
    
], debug=True)
