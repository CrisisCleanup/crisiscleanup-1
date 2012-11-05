# System libraries.
import jinja2
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')

class EditHandler(base.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    self.response.out.write(template.render(
          {"form": site_db.SiteForm(self.request.POST, site),
           "id": id,
           "page": "/edit"}))

  def post(self):
    id = int(self.request.get('_id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    data = site_db.SiteForm(self.request.POST, site)
    if data.validate():
      # Save the data, and redirect to the view page
      data.populate_obj(site);
      site.put()
      self.redirect('/dev/map')
    else:
      self.response.out.write(template.render(
          {"errors": data.errors,
           "form": data,
           "id": id,
           "page": "/edit"}))
