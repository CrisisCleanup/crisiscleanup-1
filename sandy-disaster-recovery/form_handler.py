import webapp2
import os
import jinja2
import site_db
import logging

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class FormHandler(webapp2.RequestHandler):
  def get(self):
    data = site_db.SiteForm()
    logging.critical("HEREHEREHERE\n\n\n\n")
    template_values = {"form": data,
                       "id": None,
                       "page": "/dev/"}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def post(self):
    data = site_db.SiteForm(self.request.POST)
    logging.critical("\n\n\n\n\n\nPost.")
    if data.validate():
      lookup = site_db.Site.gql(
        "WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
        name = data.name.data,
        address = data.address.data,
        zip_code = data.zip_code.data)
      site = None
      for l in lookup:
        site = l
      if not site:
              # Save the data, and redirect to the view page
        site = site_db.Site(zip_code = data.zip_code.data,
                    address = data.address.data,
                    name = data.name.data,
                    phone1 = data.phone1.data,
                    phone2 = data.phone2.data)
      data.populate_obj(site)
      site.put()
      self.get()
      return
    else:
      logging.critical("\n\n\n\n\n\nPost.")
      logging.critical("Failed to validate.")
      template_values = {"form": data,
                         "page": "/dev/",
                         "id": None}
      template = jinja_environment.get_template('form.html')
      self.response.out.write(template.render(template_values))
