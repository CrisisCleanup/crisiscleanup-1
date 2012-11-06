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
single_site_template = jinja_environment.get_template('single_site.html')
logout_template = jinja_environment.get_template('logout.html')

class EditHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    try:
      id = int(self.request.get('id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    form = site_db.SiteForm(self.request.POST, site)
    single_site = single_site_template.render(
        { "form": form })

    self.response.out.write(template.render(
          {"single_site": single_site,
           "form": form,
           "id": id,
           "page": "/edit"}))

  def AuthenticatedPost(self, org):
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    data = site_db.SiteForm(self.request.POST, site)
    if data.validate():
      # Save the data, and redirect to the view page
      data.populate_obj(site);
      site.put()
      self.redirect('/dev/map')
    else:
      single_site = single_site_template.render(
          { "form": form })

      self.response.out.write(template.render(
          {"errors": data.errors,
           "form": data,
           "id": id,
           "page": "/edit"}))
