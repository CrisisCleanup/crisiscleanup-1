# System libraries.
import jinja2
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db
def silent_none(value):
     if value is None:
         return ''
     return value

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.finalize = silent_none
template = jinja_environment.get_template('print.html')
single_site_template = jinja_environment.get_template('single_site.html')
class PrintHandler(base.AuthenticatedHandler):
  """Handler to confirm and then actually delete a site."""
  def AuthenticatedGet(self, org):
    id = int(self.request.get('id'))
    site = site_db.Site.get(db.Key.from_path('Site', id))
    template_values = {"form": site,
                       "id": id,
                       "readonly": True}
    self.response.out.write(template.render({
        "id": id,
        "form": site,
        "single_site": single_site_template.render(template_values),
        }))
