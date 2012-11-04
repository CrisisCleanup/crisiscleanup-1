#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import webapp2
import jinja2
import os

import datetime

import json as json

from wtforms.ext.appengine.db import model_form
from google.appengine.api.urlfetch import fetch

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import to_dict

#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#import django.core.handlers.wsgi
#from google.appengine.ext.db import djangoforms

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Site(db.Model):
  name = db.StringProperty(required = True)
  request_date = db.DateTimeProperty(auto_now_add=True)
  address = db.StringProperty(required = True)
  city = db.StringProperty(required = False)
  state = db.StringProperty(required = False)
  zip_code = db.IntegerProperty(required = True)
  cross_street = db.StringProperty()
  landmark = db.StringProperty()
  phone1 = db.StringProperty()
  phone2 = db.StringProperty()
  time_to_call = db.StringProperty()
  property_type = db.StringProperty(
      choices=set(["Home", "Town House", "Multi-Unit", "Business"]))
  renting = db.BooleanProperty()
  work_without_resident = db.BooleanProperty()
  ages_of_residents = db.StringProperty()
  special_needs = db.StringProperty(multiline=True)
  electricity = db.BooleanProperty()
  standing_water = db.BooleanProperty()
  tree_damage = db.BooleanProperty()
  tree_damage_details = db.StringProperty(multiline=True)
  habitable = db.BooleanProperty()
  work_requested = db.StringProperty(multiline=True)
  others_help = db.StringProperty(multiline=True)
  debris_removal_only = db.BooleanProperty()
  work_type = db.StringProperty(choices=set(["Flood", "Trees", "Other"]))
  tree_diameter = db.StringProperty()
  electrical_lines = db.BooleanProperty()
  cable_lines = db.BooleanProperty()
  cutting_cause_harm = db.BooleanProperty()
  other_hazards = db.StringProperty(multiline = True)
  insurance = db.StringProperty(multiline = True)
  notes = db.StringProperty(multiline = True)
  latitude = db.FloatProperty()
  longitude = db.FloatProperty()


site_form_w = model_form(Site)

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

class MainHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {
        "sites" : [json.dumps(dict(to_dict(site).items() + [("id", site.key().id())]), default=dthandler) for site in Site.all()],
        "filters" : [
            ["debris_only", "Remove Debris Only"],
            ["electricity", "Has Electricity"],
            ["no_standing_water", "No Standing Water"],
            ["not_habitable", "Home is not habitable"],
            ["Flood", "Primary problem is flood damage"],
            ["Trees", "Primary problem is trees"],
            ["NJ", "New Jersey"],
            ["NY", "New York"]],
        }

    template = jinja_environment.get_template('main.html')
    self.response.out.write(template.render(template_values))

class FormHandler(webapp2.RequestHandler):
  def get(self):
    data = site_form_w(self.request.POST)
    template_values = {"form": data,
                       "id": None,
                       "page": "/"}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))


  def post(self):
    data = site_form_w(self.request.POST)
    if data.validate():
      lookup = Site.gql("WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
                        name = data.name.data,
                        address = data.address.data,
                        zip_code = data.zip_code.data)
      site = None
      for l in lookup:
        site = l
      if not site:
              # Save the data, and redirect to the view page
        site = Site(zip_code = data.zip_code.data,
                    address = data.address.data,
                    name = data.name.data,
                    phone1 = data.phone1.data,
                    phone2 = data.phone2.data)
      data.populate_obj(site)

      site.put()
      self.get()
    else:
      template_values = {"form": data}
      template = jinja_environment.get_template('form.html')
      self.response.out.write(template.render(template_values))

class SitesPage(webapp.RequestHandler):
  def get(self):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    for site in query:
      self.response.out.write('<a href="/edit?id=%d">Edit</a> - ' %
                              site.key().id())
      self.response.out.write("%s - %s<br />" %
                              (site.name, site.address))

class EditPage(webapp.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    site = Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site_form_w(self.request.POST, site),
                       "id": id}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def post(self):
    id = int(self.request.get('_id'))
    site = Site.get(db.Key.from_path('Site', id))
    data = site_form_w(self.request.POST, site)
    if data.validate():
      # Save the data, and redirect to the view page
      data.populate_obj(site);
      site.put()
      self.redirect('/map')
    else:
      template_values = {"form": data,
                         "id": id,
                         "page": "/edit"}
      template = jinja_environment.get_template('form.html')
      self.response.out.write(template.render(template_values))

class ImportHandler(webapp.RequestHandler):
  def get(self):
    f = fetch("https://script.googleusercontent.com/echo?user_content_key=FhDerHYRqmPomvddrWG5z1EPE2M6pIsdWoneKZggh5tOOwrmP4Atbge70tQMNTIGyGqIpA2WfT2mn-b9xDGva0ig28c7dyAJm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnLQWLGh0dZkw6EUdDCIUunrCvAUHV5O19lgdOMElR3BpzsNnsNxUs69kLAqLclCCiDOmbnRGq-tk&lib=MIG37R_y3SDE8eP6TP_JVJA0rWYMbTwle");
    if f.status_code == 200:

      c = f.content.replace("var sites = ", "", 1).replace(";", "")
      all_sites = json.loads(c)
      for s in all_sites:
        self.response.write(s["Resident Name"] + "<br />")
        if not s["Zip Code"]:
          s["Zip Code"] = 0
        lookup = Site.gql("WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
                          name = s["Resident Name"],
                          address = s["Address"],
                          zip_code = int(s["Zip Code"]))
        site = None
        for l in lookup:
          site = l
        if not site:
          # Save the data, and redirect to the view page
          site = Site(address = s["Address"],
                      name = s["Resident Name"],
                      phone1 = str(s["Contact # s (Home and Cell)"]),
                      city = s["City"],
                      state = s["State"],
                      zip_code = int(s["Zip Code"]),
                      cross_street = s["Cross Street/ Landmark"],
                      time_to_call = s["Best Time to call"],
                      habitable = "yes" in s["Is Home Habitable?"].lower(),
                      electricity = "yes" in s["Is electricity available on site?"].lower(),
                      debris_only = "yes" in s["Are you only requesting Debris removal?"].lower(),
                      standing_water = "yes" in s["Standing water on site?"].lower(),
                      work_requested = s["Work Requested"])
        if s["Lat, Long"]:
          lls = s["Lat, Long"].split(",")
          if len(lls) == 2:
            site.latitude = float(lls[0])
            site.longitude = float(lls[1])

        site.put()

class MapRedirectHandler(webapp.RequestHandler):
  def get(self):
    self.redirect("http://maps.google.com/?q=http://www.aarontitus.net/maps/sandy_work_orders.kmz")
  
class SpreadsheetRedirectHandler(webapp.RequestHandler):
  def get(self):
    self.redirect("https://docs.google.com/spreadsheet/ccc?key=0AhBdPrWyrhIfdFVHMDFOc0NCQjNNbmVvNHJybTlBUXc#gid=0")


app = webapp2.WSGIApplication([
    ('/map', MapRedirectHandler),
    ('/dev/map', MainHandler),
    ('/dev/', FormHandler),
    ('/', SpreadsheetRedirectHandler),
    ('/edit', EditPage),
    ('/import', ImportHandler),
    ('/sites', SitesPage)
], debug=True)
