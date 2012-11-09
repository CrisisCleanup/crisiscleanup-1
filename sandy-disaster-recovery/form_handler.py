# System libraries.
import cgi
import jinja2
import logging
import os
import urllib2

# Local libraries.
import base
import event_db
import site_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site.html')
logout_template = jinja_environment.get_template('logout.html')

class FormHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    message = cgi.escape(self.request.get("message"))
    if len(message) == 0:
      message = None
    form = site_db.SiteForm()
    single_site = single_site_template.render(
        { "form": form })
    event_name = self.request.get(
        "event_name", default_value = event_db.DefaultEventName())
    event = event_db.Event.get_by_key_name(event_name)
    if event:
      event_name = event.name
    self.response.out.write(template.render(
        {"message" : message,
         "logout" : logout_template.render({"org": org}),
         "single_site" : single_site,
         "form": site_db.SiteForm(),
         "id": None,
         "page": "/",
         "event_name": event_name}))

  def AuthenticatedPost(self, org):
    data = site_db.SiteForm(self.request.POST)
    message = ""
    event_name = self.request.get("event_name",
                                  default_value = event_db.DefaultEventName())

    if data.validate():
      lookup = site_db.Site.gql(
        "WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
        name = data.name.data,
        address = data.address.data,
        zip_code = data.zip_code.data)
      site = None
      for l in lookup:
        # See if this same site is for a different event.
        # If so, we'll make a new one.
        if not site.event or site.event.name != event_name:
          site = l

      if not site:
        # Save the data, and redirect to the view page
        site = site_db.Site(zip_code = data.zip_code.data,
                            address = data.address.data,
                            name = data.name.data,
                            phone1 = data.phone1.data,
                            phone2 = data.phone2.data)
      data.populate_obj(site)
      site.reported_by = org
      if not site.event and event_db.AddSiteToEvent(site, event_name):
        self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
        return
      else:
        message = "Failed to add site to event: " + event_name
    single_site = single_site_template.render(
        { "form": data })
    self.response.out.write(template.render(
        {"message": message,
         "errors": data.errors,
         "logout" : logout_template.render({"org": org}),
         "single_site": single_site,
         "form": data,
         "id": None,
         "page": "/",
         "event_name": event_name}))
