# System libraries.
import datetime
import jinja2
import json
import os
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app

# Local libraries.
import authentication_handler
import base
import delete_handler
import edit_handler
import form_handler
import import_handler
import key
import map_handler
import print_handler
import problem_handler
import site_api_handler
import sites_handler

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MapRedirectHandler(base.RequestHandler):
  def get(self):
    self.redirect("http://maps.google.com/?q=http://www.aarontitus.net/maps/sandy_work_orders.kmz")

class LogoutHandler(base.RequestHandler):
  def get(self):
    self.response.headers.add_header("Set-Cookie",
                                     key.GetDeleteCookie())
    self.redirect("/authentication")

class SpreadsheetRedirectHandler(base.RequestHandler):
  def get(self):
    self.redirect("https://docs.google.com/spreadsheet/ccc?key=0AhBdPrWyrhIfdFVHMDFOc0NCQjNNbmVvNHJybTlBUXc#gid=0")

app = webapp2.WSGIApplication([
    ('/api/site', site_api_handler.SiteApiHandler),
    ('/authentication', authentication_handler.AuthenticationHandler),
    ('/logout', LogoutHandler),
    ('/', SpreadsheetRedirectHandler),
    ('/delete', delete_handler.DeleteHandler),
    ('/dev/', form_handler.FormHandler),
    ('/dev/map', map_handler.MapHandler),
    ('/edit', edit_handler.EditHandler),
    ('/import', import_handler.ImportHandler),
    ('/map', MapRedirectHandler),
    ('/print', print_handler.PrintHandler),
    ('/problems', problem_handler.ProblemHandler),
    ('/sites', sites_handler.SitesHandler)
], debug=True)
