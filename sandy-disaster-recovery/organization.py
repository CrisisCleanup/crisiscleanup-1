from google.appengine.ext import db

class Organization(db.Model):
  # Data about the organization.
  name = db.StringProperty(required = True)
  # We store passwords in plain text, because we want to
  # set the passwords ourselves, and may need to be able
  # to retrieve them for an organization.
  password = db.StringProperty(required = True)
  primary_contact_email = db.StringProperty(default = '')
