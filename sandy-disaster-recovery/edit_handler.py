# System libraries.
import jinja2
import logging
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
  def AuthenticatedGet(self, org, event):
    try:
      id = int(self.request.get('id'))
    except:
      self.response.set_status(404)
      return
    site = site_db.GetAndCache(id)
    if not site:
      self.response.set_status(404)
      return
    form = site_db.SiteForm(self.request.POST, site)
    single_site = single_site_template.render(
        { "form": form,
          "org": org})

    self.response.out.write(template.render(
          {"mode_js": self.request.get("mode") == "js",
           "single_site": single_site,
           "form": form,
           "id": id,
           "page": "/edit"}))

  def AuthenticatedPost(self, org, event):
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get_by_id(id)
    data = site_db.SiteForm(self.request.POST, site)
    case_number = site.case_number
    claim_for_org = self.request.get("claim_for_org") == "y"

    mode_js = self.request.get("mode") == "js"
    if data.validate():
      # Save the data, and redirect to the view page
      for f in data:
        # In order to avoid overriding fields that didn't appear
        # in this form, we have to only set those that were explicitly
        # set in the post request.
        in_post = self.request.get(f.name, default_value = None)
        if not in_post:
          continue
        setattr(site, f.name, f.data)
      if claim_for_org:
        site.claimed_by = org
      site_db.PutAndCache(site)
      if mode_js:
        # returning a 200 is sufficient here.
        return
      else:
        self.redirect('/map')
    else:
      single_site = single_site_template.render(
          { "form": data,
            "org": org})
      if mode_js:
        self.response.set_status(400)
      self.response.out.write(template.render(
          {"mode_js": mode_js,
           "errors": data.errors,
           "form": data,
           "single_site": single_site,
           "id": id,
           "page": "/edit"}))
