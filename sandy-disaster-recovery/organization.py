from google.appengine.ext import db

import cache

class Organization(db.Model):
  # Data about the organization.
  name = db.StringProperty(required = True)
  # We store passwords in plain text, because we want to
  # set the passwords ourselves, and may need to be able
  # to retrieve them for an organization.
  password = db.StringProperty(required = True)
  primary_contact_email = db.StringProperty(default = '')
  # If set, then only session cookies are sent to the
  # user's browser. Otherwise, they'll receive cookies that
  # will expire in 1 week.
  only_session_authentication = db.BooleanProperty(default = True)

def GetCached(org_id):
  one_hour_in_seconds = 3600
  return cache.GetCachedById(Organization, one_hour_in_seconds, org_id)

def GetAllCached():
  two_minutes = 120
  return cache.GetAllCachedBy(Organization, two_minutes)
