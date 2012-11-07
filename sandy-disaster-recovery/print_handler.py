# System libraries.
import jinja2
import logging
import math
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
print_single_template = jinja_environment.get_template('print_single.html')
class PrintHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    if not len(self.request.get('id')):
      sites = [site for site in site_db.Site.all()]
    else:
      try:
        ids = [int(id) for id in self.request.get('id').split(',')]
      except:
        return
      sites = [site for site in site_db.Site.get_by_id(ids)]
    content = ""
    first_time = True
    for site in sites:
      template_values = {"form": site,
                         "id": site.key().id(),
                         "readonly": True}
      content += print_single_template.render({
          "page_break": not first_time,
          "show_map": math.fabs(site.latitude) > 0,
          "id": site.key().id(),
          "form": site,
          "single_site": single_site_template.render(template_values),
          })
      first_time = False
    self.response.out.write(template.render({
        "content": content
        }))
