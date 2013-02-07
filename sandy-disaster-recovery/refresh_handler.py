# System libraries.
from google.appengine.ext import db
import logging
# Local libraries.
import base
import event_db
import site_db

class RefreshHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    q = db.Query(site_db.Site)
    counties = set([proj.county for proj in q.run(batch_size = 2000)])
    counties.add("")
    event_db.SetCountiesForEvent(event.key().id(), counties)
    self.response.out.write(
        "<br />".join(["<a href='/sites?county=%s'>County: '%s'</a>" % (county, county)
         for county in counties]))
