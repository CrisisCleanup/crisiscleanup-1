import jinja2
import logging
import os
import site_db
import webapp2
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class DeleteHandler(webapp2.RequestHandler):
  """Handler to confirm and then actually delete a site."""
  def get(self):
    id = int(self.request.get('id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site_db.SiteForm(self.request.POST, site),
                       "id": id,
                       "delete": True}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def post(self):
    id = int(self.request.get('_id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    if site:
      site.delete()
    self.redirect('/sites')
