# System libraries.
import Cookie
import datetime
import jinja2
import os
import urllib
from google.appengine.ext import db
import random
import string
import wtforms.fields
import wtforms.form
import wtforms.validators
import logging

# Local libraries.
import base
import event_db
import key
import organization
import site_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('authentication.html')

def GetOrganizationForm(post_data):
  organizations = organization.GetAllCached()
  events = event_db.GetAllCached()
  dirty = False
  if not len(organizations):
    # This is to initially populate the database the first time.
    # TODO(oryol): Add a regular Google login-authenticated handler
    # to add users and passwords, whitelisted to the set of e-mail
    # addresses we want to allow.
    default = organization.Organization(name = "Administrator",
                                        password = "temporary_password")
    default.put()
    organizations.append(default)
  elif len(organizations) >= 2:
    modified = []
    for o in organizations:
      if o.name == "Administrator":
        o.delete()
      else:
        modified.append(o)
    organizations = modified

  if not len(events):
    logging.warning("Initialize called")
    e = event_db.Event(name = event_db.DefaultEventName(),
                       case_label = "A")
    e.put()
    # TODO(Jeremy): This could be dangerous if we reset events.
    for s in site_db.Site.all():
      event_db.AddSiteToEvent(s, e.key().id(), force = True)
    events = [e]

  class OrganizationForm(wtforms.form.Form):
    name = wtforms.fields.SelectField(
        'Name',
        choices = [(o.name, o.name) for o in organizations],
        validators = [wtforms.validators.required()])
    event = wtforms.fields.SelectField(
        'Work Event',
        choices = [(e.name, e.name) for e in events],
        validators = [wtforms.validators.required()])
    password = wtforms.fields.PasswordField(
        'Password',
        validators = [ wtforms.validators.required() ])
  form = OrganizationForm(post_data)
  return form


class AuthenticationHandler(base.RequestHandler):
  def get(self):
    org, event = key.CheckAuthorization(self.request)
    if org and event:
      self.redirect(self.request.get('destination', default_value='/'))
      return

    self.response.out.write(template.render({
      "form" : GetOrganizationForm(self.request.POST),
      "destination" : self.request.get('destination', default_value='/'),
      "page" : "/authentication",
    }))

  def post(self):
    now = datetime.datetime.now()
    form = GetOrganizationForm(self.request.POST)
    if not form.validate():
      self.redirect('/authentication')
    org = None
    for l in organization.Organization.gql(
        "WHERE name = :name LIMIT 1", name = form.name.data):
      org = l
    event = None
    logging.critical("Event: " + form.event.data)
    for e in event_db.Event.gql(
      "WHERE name = :name LIMIT 1", name = form.event.data):
      event = e
      logging.critical(event.name)
      logging.critical(event.key())
      logging.critical(event.key().id())
    if event and org and org.password == form.password.data:
      keys = key.Key.all()
      keys.order("date")
      selected_key = None
      for k in keys:
        age = now - k.date
        # Only use keys created in about the last day,
        # and garbage collect keys older than 2 days.
        if age.days > 14:
          k.delete()
        elif age.days <= 1:
          selected_key = k
      if not selected_key:
        selected_key = key.Key(
            secret_key = ''.join(random.choice(
                string.ascii_uppercase + string.digits)
                                  for x in range(20)))
        selected_key.put()
      logging.critical('Cookie: ' + event.name + org.name)
      self.response.headers.add_header("Set-Cookie",
                                       selected_key.getCookie(org, event))
      self.redirect(urllib.unquote(self.request.get('destination', default_value='/').encode('ascii')))
    else:
      self.redirect(self.request.url)
