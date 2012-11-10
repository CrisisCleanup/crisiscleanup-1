# System libraries.
import jinja2
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteHandler(base.AuthenticatedHandler):
  """Handler to confirm and then actually delete a site."""
  def AuthenticatedGet(self, org, event):
    try:
      id = int(self.request.get('id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site_db.SiteForm(self.request.POST, site),
                       "id": id,
                       "delete": True}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def AuthenticatedPost(self, org, event):
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get(db.Key.from_path('Site', id))
    if site:
      site.delete()
    self.redirect('/sites')
