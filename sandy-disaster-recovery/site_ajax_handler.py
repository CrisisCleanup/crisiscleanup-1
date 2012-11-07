# System libraries.
import datetime
import jinja2
import json
import os
from google.appengine.ext.db import to_dict
from google.appengine.ext import db

# Local libraries.
import base
import key
import map_handler
import site_db

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class SiteAjaxHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    try:
      id = int(self.request.get('id'))
    except:
      self.response.set_status(404)
      return
    site = site_db.Site.get_by_id(id)
    if not site:
      self.response.set_status(404)
      return
    # TODO(jeremy): Add the various fixes for Flash
    # and other vulnerabilities caused by having user-generated
    # content in JSON strings, by setting this as an attachment
    # and prepending the proper garbage strings.
    # Javascript security is really a pain.
    self.response.out.write(
        json.dumps(map_handler.SiteToDict(site), default = dthandler))
