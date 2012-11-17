# System libraries.
import datetime
import jinja2
import json
import os
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from google.appengine.api import memcache

# Local libraries.
import base
import key
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class SiteAjaxHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    id_param = self.request.get('id')
    if id_param == "all":
      county = self.request.get("county", default_value = "all")
      output = json.dumps(
        [s[1] for s in site_db.GetAllCached(event, county)],
        default=dthandler)
      self.response.out.write(output)
      return
    try:
      id = int(id_param)
    except:
      self.response.set_status(404)
      return
    site = site_db.GetAndCache(id)
    if not site:
      self.response.set_status(404)
      return
    # TODO(jeremy): Add the various fixes for Flash
    # and other vulnerabilities caused by having user-generated
    # content in JSON strings, by setting this as an attachment
    # and prepending the proper garbage strings.
    # Javascript security is really a pain.
    self.response.out.write(
        json.dumps(site_db.SiteToDict(site), default = dthandler))
