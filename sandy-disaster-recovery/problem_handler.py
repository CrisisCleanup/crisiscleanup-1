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
  return s.case_number

class ProblemHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    query = db.GqlQuery("SELECT * FROM Site ORDER BY name")
    ordered = sorted(query, key = lambda s: ProblemSeverity(s))
    for s in ordered:
      self.response.out.write('<a href="/edit?id=%d">Edit</a> - ' %
                              s.key().id())
      self.response.out.write("%s: %s - %s<br />" %
                              (s.case_number, s.name, s.address))
