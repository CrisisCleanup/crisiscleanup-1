#!/usr/bin/env python

# from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import datetime
import jinja2
import json
import os
import webapp2

# Local imports
import delete_handler
import edit_handler
import form_handler
import import_handler
import map_handler
import problem_handler
import sites_handler

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
    ('/', SpreadsheetRedirectHandler),
    ('/delete', delete_handler.DeleteHandler),
    ('/dev/', form_handler.FormHandler),
    ('/dev/map', map_handler.MapHandler),
    ('/edit', edit_handler.EditHandler),
    ('/import', import_handler.ImportHandler),
    ('/map', MapRedirectHandler),
    ('/problems', problem_handler.ProblemHandler),
    ('/sites', sites_handler.SitesHandler)
], debug=True)

