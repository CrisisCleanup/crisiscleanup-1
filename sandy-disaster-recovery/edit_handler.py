import webapp2

class EditHandler(webapp2.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    site = Site.get(db.Key.from_path('Site', id))
    template_values = {"form": SiteForm(self.request.POST, site),
                       "id": id}
    template = jinja_environment.get_template('form.html')
    self.response.out.write(template.render(template_values))

  def post(self):
    id = int(self.request.get('_id'))
    site = Site.get(db.Key.from_path('Site', id))
    data = site_form_w(self.request.POST, site)
    if data.validate():
      # Save the data, and redirect to the view page
      data.populate_obj(site);
      site.put()
      self.redirect('/map')
    else:
      template_values = {"form": data,
                         "id": id,
                         "page": "/edit"}
      template = jinja_environment.get_template('form.html')
      self.response.out.write(template.render(template_values))
