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
import initialize_handler
import map_handler
import print_handler
import problem_handler
import site_ajax_handler
import site_api_handler
import sites_handler

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
    Route(r'/', redirect_to=SPREADSHEET_URL, name='spreadsheet_redirect'),
    Route(r'/api/site', site_api_handler.SiteApiHandler, 'site_api'),
    Route(r'/api/site_ajax', site_ajax_handler.SiteAjaxHandler, 'site_ajax'),
    Route(r'/authentication', authentication_handler.AuthenticationHandler,
          'auth'),
    Route(r'/export', export_handler.ExportHandler, 'export'),
    Route(r'/logout', LogoutHandler, 'logout'),
    Route(r'/delete', delete_handler.DeleteHandler, 'delete'),
    Route(r'/dev', form_handler.FormHandler, 'dev'),
    Route(r'/dev/map', map_handler.MapHandler, 'map'),
    Route(r'/dev/maps', redirect_to_name='map', name='maps_redirect'),
    Route(r'/edit', edit_handler.EditHandler, 'edit'),
    Route(r'/import', import_handler.ImportHandler, 'import'),
    Route(r'/initialize', initialize_handler.InitializeHandler, 'initialize'),
    Route(r'/map', redirect_to=MAP_URL, name='external_map_redirect'),
    Route(r'/maps', redirect_to_name=MAP_URL, name='external_maps_redirect'),
    Route(r'/print', print_handler.PrintHandler, 'print'),
    Route(r'/problems', problem_handler.ProblemHandler, 'problems'),
    Route(r'/sites', sites_handler.SitesHandler, 'sites')
], debug=True)
