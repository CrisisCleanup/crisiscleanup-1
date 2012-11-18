# System libraries.
import cgi
import jinja2
import logging
import os
import urllib2
import wtforms.validators

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
  def AuthenticatedGet(self, org, event):
    message = cgi.escape(self.request.get("message"))
    if len(message) == 0:
      message = None
    form = site_db.SiteForm()
    single_site = single_site_template.render(
        { "form": form,
          "org": org})
    self.response.out.write(template.render(
        {"version" : os.environ['CURRENT_VERSION_ID'],
         "message" : message,
         "logout" : logout_template.render({"org": org}),
         "single_site" : single_site,
         "form": site_db.SiteForm(),
         "id": None,
         "page": "/",
         "event_name": event.name}))

  def AuthenticatedPost(self, org, event):
    data = site_db.SiteForm(self.request.POST)
    extra_validators = {
      "name": wtforms.validators.Length(min = 1, max = 100),
      "city": wtforms.validators.Length(min = 1, max = 100),
      "state": wtforms.validators.Length(min = 1, max = 100),
      "phone1": wtforms.validators.Length(min = 1, max = 100,
                                          message = "Please provide a primary phone number"),
      "primary_work_type": wtforms.validators.Length(min = 1, max = 100,
                                                     message = "Please select the primary work type."),      
    }
    data.name.validators += (wtforms.validators.Length(min = 1, max = 100,
                             message = "Name must be between 1 and 100 characters"),)
    data.phone1.validators += (wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a primary phone number"),)
    data.city.validators += (wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a city name"),)
    data.state.validators += (wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a state name"),)
    data.work_type.validators += (wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please set a primary work type"),)
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
        if l.event and l.event.name == event.name:
          site = l
          break

      if not site:
        # Save the data, and redirect to the view page
        site = site_db.Site(zip_code = data.zip_code.data,
                            address = data.address.data,
                            name = data.name.data,
                            phone1 = data.phone1.data,
                            phone2 = data.phone2.data)
      data.populate_obj(site)
      site.reported_by = org
      if site.event or event_db.AddSiteToEvent(site, event.key().id()):
        self.redirect("/?message=" + "Successfully added " + urllib2.quote(site.name))
        return
      else:
        message = "Failed to add site to event: " + event.name
    else:
      message = "Failed to validate"
    single_site = single_site_template.render(
        { "form": data,
          "org": org})
    self.response.out.write(template.render(
        {"message": message,
         "version" : os.environ['CURRENT_VERSION_ID'],
         "errors": data.errors,
         "logout" : logout_template.render({"org": org}),
         "single_site": single_site,
         "form": data,
         "id": None,
         "page": "/",
         "event_name": event.name}))
