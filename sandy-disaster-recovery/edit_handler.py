import webapp2
import site_db
import os
import jinja2
from google.appengine.ext import db
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class EditHandler(webapp2.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site_db.SiteForm(self.request.POST, site),
                       "id": id}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

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
      template_values = {"form": data,
                         "id": id,
                         "page": "/edit"}
      template = jinja_environment.get_template('form.html')
      self.response.out.write(template.render(template_values))
