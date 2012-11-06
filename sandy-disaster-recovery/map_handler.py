# System libraries.
import datetime
import jinja2
import json
import os
from google.appengine.ext.db import to_dict

# Local libraries.
import base
import key
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('main.html')
class MapHandler(base.RequestHandler):
  def get(self):
    filters = [
              ["debris_only", "Remove Debris Only"],
              ["electricity", "Has Electricity"],
              ["no_standing_water", "No Standing Water"],
              ["not_habitable", "Home is not habitable"],
              ["Flood", "Primary problem is flood damage"],
              ["Trees", "Primary problem is trees"],
              ["NJ", "New Jersey"],
              ["NY", "New York"]]

    org = key.CheckAuthorization(self.request)
    if org:
      template_values = {
          "sites" :
            [json.dumps(dict(to_dict(s).items() +
                             [("id", s.key().id())]),
                        default=dthandler)
             for s in site_db.Site.all()],
          "status_choices" : [json.dumps(c) for c in site_db.STATUS_CHOICES],
          "filters" : filters,
          "demo" : False,
        }
    else:
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
                 }) for s in site_db.Site.all()],
          "filters" : filters,
          "demo" : True,
        }
    self.response.out.write(template.render(template_values))
