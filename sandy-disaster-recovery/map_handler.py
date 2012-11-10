# System libraries.
import datetime
import jinja2
import json
import os
from google.appengine.ext import db
from google.appengine.api import memcache

# Local libraries.
import base
import event_db
import key
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('main.html')
logout_template = jinja_environment.get_template('logout.html')
class MapHandler(base.RequestHandler):
  def get(self):
    filters = [
              ["debris_only", "Remove Debris Only"],
              ["electricity", "Has Electricity"],
              ["no_standing_water", "No Standing Water"],
              ["not_habitable", "Home is not habitable"],
              ["Flood", "Primary problem is flood damage"],
              ["Trees", "Primary problem is trees"],
              ["Goods or Services", "Primary need is goods and services"],
              ["CT", "Connecticut"],
              ["NJ", "New Jersey"],
              ["NY", "New York"]]

    org, event = key.CheckAuthorization(self.request)
    if org:
      filters = [["claimed", "Claimed by " + org.name],
                 ["unclaimed", "Unclaimed"],
                 ["open", "Open"],
                 ["closed", "Closed"],
                 ["reported", "Reported by " + org.name],
                 ] + filters
      template_values = {
          "org" : org,
          "logout" : logout_template.render({"org": org,
                                             "include_search": True}),
          "status_choices" : [json.dumps(c) for c in
                              site_db.Site.status.choices],
          "filters" : filters,
          "demo" : False,
        }
    else:
      # Allow people to bookmark an unauthenticated event map,
      # by setting the event ID.
      event = event_db.GetEventFromParam(self.request.get("event_id"))
      if not event:
        self.response.set_status(404)
        return
      template_values = {
          "sites" :
             [json.dumps({
                 "latitude": round(s.latitude, 2),
                 "longitude": round(s.longitude, 2),
                 "debris_removal_only": s.debris_removal_only,
                 "electricity": s.electricity,
                 "standing_water": s.standing_water,
                 "tree_damage": s.tree_damage,
                 "habitable": s.habitable,
                 "electrical_lines": s.electrical_lines,
                 "cable_lines": s.cable_lines,
                 "cutting_cause_harm": s.cutting_cause_harm,
                 "work_type": s.work_type,
                 "state": s.state,
                 }) for s in [p[0] for p in site_db.GetAllCached(event)]],
          "filters" : filters,
          "demo" : True,
        }
    self.response.out.write(template.render(template_values))
