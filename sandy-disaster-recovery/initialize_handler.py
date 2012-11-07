# System libraries.
import logging
from google.appengine.ext import db

# Local libraries.
import base
import event_db
import site_db

class InitializeHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    logging.warning("Initialize called by " + org.name)
    events = [e for e in event_db.Event.all()]
    if len(events):
      logging.critical("Double initialization by " + org.name)
      self.response.set_status(404)
      return
    event = event_db.Event(key_name = event_db.DefaultEventName(),
                           name = event_db.DefaultEventName(),
                           case_label = "A")
    event.put()
    for s in site_db.Site.all():
      event_db.AddSiteToEvent(s, event.name)
    self.response.out.write("Initialized")
