# System libraries.
import datetime
import json
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db

class SitesHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    for s in query:
      self.response.out.write(
          '<a href="/edit?id=%(id)s">Edit</a> '
          '<a href="/delete?id=%(id)s">Delete</a> - ' % {'id' : s.key().id() })
      self.response.out.write("%s: %s - %s<br />" %
                              (s.case_number, s.name, s.address))
