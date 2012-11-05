# System libraries.
import datetime
import jinja2
import json
import os
from google.appengine.ext.db import to_dict

# Local libraries.
import base
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MapHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    template_values = {
        "sites" :
          [json.dumps(dict(to_dict(s).items() +
                           [("id", s.key().id())]),
                      default=dthandler)
           for s in site_db.Site.all()],
        "filters" : [
            ["debris_only", "Remove Debris Only"],
            ["electricity", "Has Electricity"],
            ["no_standing_water", "No Standing Water"],
            ["not_habitable", "Home is not habitable"],
            ["Flood", "Primary problem is flood damage"],
            ["Trees", "Primary problem is trees"],
            ["NJ", "New Jersey"],
            ["NY", "New York"]],
        }

    template = jinja_environment.get_template('main.html')
    self.response.out.write(template.render(template_values))
