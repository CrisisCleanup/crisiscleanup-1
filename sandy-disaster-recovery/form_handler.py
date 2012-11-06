# System libraries.
import jinja2
import os

# Local libraries.
import base
import site_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')

class FormHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    message = self.request.get("message", default_value = None)
    self.response.out.write(template.render(
        {"message" : message,
         "form": site_db.SiteForm(),
         "id": None,
         "page": "/dev/"}))

  def post(self):
    data = site_db.SiteForm(self.request.POST)
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
      self.redirect("/dev/?message=" + "Successfully added " + site.name)
    else:
      self.response.out.write(template.render(
          {"errors": data.errors,
           "form": data,
           "id": None,
           "page": "/dev/"}))
