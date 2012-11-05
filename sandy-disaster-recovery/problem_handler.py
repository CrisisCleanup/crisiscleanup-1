# System libraries.
import datetime
import json
import math
import os
from google.appengine.ext import db

# Local libraries.
import base
import site_db

def ProblemSeverity(s):
  distance = math.sqrt(math.pow(s.latitude - 39.5, 2) + math.pow(s.longitude + 75, 2))
  return -distance

class ProblemHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    ordered = sorted(query, key = lambda s: ProblemSeverity(s))
    for s in ordered:
      self.response.out.write('<a href="/edit?id=%d">Edit</a> - ' %
                              s.key().id())
      self.response.out.write("%s - %s<br />" %
                              (s.name, s.address))
