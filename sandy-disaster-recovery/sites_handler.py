import webapp2

import os
import json
import datetime
from google.appengine.ext import db
import site_db

class SitesHandler(webapp2.RequestHandler):
  def get(self):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    for s in query:
      self.response.out.write(
          '<a href="/edit?id=%(id)s">Edit</a> '
          '<a href="/delete?id=%(id)s">Delete</a> - ' % {'id' : s.key().id() })
      self.response.out.write("%s - %s<br />" %
                              (s.name, s.address))
