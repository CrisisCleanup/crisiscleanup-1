#!/usr/bin/env python



# from google.appengine.ext import webapp

from google.appengine.ext.webapp.util import run_wsgi_app

import datetime
import jinja2
import json as json
import os
import webapp2

# Local imports
import map_handler
import edit_handler
import form_handler
import sites_handler
import import_handler
import problem_handler

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

class MapRedirectHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect("http://maps.google.com/?q=http://www.aarontitus.net/maps/sandy_work_orders.kmz")

class SpreadsheetRedirectHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect("https://docs.google.com/spreadsheet/ccc?key=0AhBdPrWyrhIfdFVHMDFOc0NCQjNNbmVvNHJybTlBUXc#gid=0")

app = webapp2.WSGIApplication([
    ('/map', MapRedirectHandler),
    ('/problems', problem_handler.ProblemHandler),
    ('/dev/map', map_handler.MapHandler),
    ('/dev/', form_handler.FormHandler),
    ('/', SpreadsheetRedirectHandler),
    ('/edit', edit_handler.EditHandler),
    ('/import', import_handler.ImportHandler),
    ('/sites', sites_handler.SitesHandler)
], debug=True)

