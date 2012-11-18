from google.appengine.ext import db
import Cookie
import datetime
import hashlib
import logging
import organization
from google.appengine.api import memcache

# Local classes
import cache
import event_db

class Key(db.Model):
  secret_key = db.StringProperty(required = True)
  date = db.DateTimeProperty(required = True, auto_now_add = True)

  def hashOrganization(self, org):
    h = hashlib.md5()
    h.update(self.secret_key)
    h.update(org.name)
    h.update(org.password)
    h.update(str(self.key().id()))
    return h.hexdigest()

  def getCookie(self, org, event):
    cookie = Cookie.SimpleCookie("")
    cookie["sandy-recovery-auth"] = (
        ":".join([self.hashOrganization(org),
                  str(self.key().id()),
                  str(org.key().id()),
                  str(event.key().id())]))
    cookie["sandy-recovery-auth"]["domain"] = ""
    if not org.only_session_authentication:
      expires = datetime.datetime.now() + datetime.timedelta(days = 7)
      cookie["sandy-recovery-auth"]["expires"] = (
          expires.strftime('%a, %d %b %Y %H:%M:%S'))
    return str(cookie)

one_week_in_seconds = 604800
def GetCached(key_id):
  return cache.GetCachedById(Key, one_week_in_seconds, key_id)

def GetAndCache(key_id):
  return cache.GetAndCache(Key, one_week_in_seconds, key_id)

def GetDeleteCookie():
  cookie = Cookie.SimpleCookie("")
  cookie["sandy-recovery-auth"] = ""
  cookie["sandy-recovery-auth"]["domain"] = ""
  expires = datetime.datetime.now() - datetime.timedelta(days = 7)
  cookie["sandy-recovery-auth"]["expires"] = (
      expires.strftime('%a, %d %b %Y %H:%M:%S'))
  return str(cookie)

def getIntOrNone(s):
  try:
    return int(s)
  except ValueError:
    return None


def CheckAuthorization(request):
  if "Cookie" in request.headers.keys():
    cookie = Cookie.SimpleCookie(request.headers["Cookie"])
    if "sandy-recovery-auth" in cookie.keys():
      contents = cookie["sandy-recovery-auth"].value
      if contents:
        parts = contents.split(":")
        if len(parts) == 4:
          event_id = getIntOrNone(parts[3])
          org_id = getIntOrNone(parts[2])
          key_id = getIntOrNone(parts[1])
          if org_id and key_id and event_id:
            org_key = cache.GetKey(organization.Organization, org_id)
            key_key = cache.GetKey(Key, key_id)
            event_key = cache.GetKey(event_db.Event, event_id)

            results = memcache.get_multi([org_key, key_key, event_key])
            org = results.get(org_key)
            key = results.get(key_key)
            event = results.get(event_key)
            if not org:
              org = organization.GetAndCache(org_id)
            if not key:
              key = GetAndCache(key_id)
            if not event:
              event = event_db.GetAndCache(event_id)
            # Check the age of the key, and delete it
            # if it is too old.
            if key:
              age = datetime.datetime.now() - key.date
              if age.days > 14:
                key.delete()
                key = None
            if org and key and event:
              if (parts[0] == key.hashOrganization(org)):
                return org, event
  return None, None
