import webapp2

import os
import json
import datetime
from google.appengine.ext import db
import site_db
import math

def ProblemSeverity(s):
  distance = math.sqrt(math.pow(s.latitude - 39.5, 2) + math.pow(s.longitude + 75, 2))
  return -distance

class ProblemHandler(webapp2.RequestHandler):
  def get(self):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    ordered = sorted(query, key = lambda s: ProblemSeverity(s))
    for s in ordered:
      self.response.out.write('<a href="/edit?id=%d">Edit</a> - ' %
                              s.key().id())
      self.response.out.write("%s - %s<br />" %
                              (s.name, s.address))
