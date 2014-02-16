import webapp2
import add_permissions_schema_update
from google.appengine.ext import deferred

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(add_permissions_schema_update.AddPermissionsSchemaUpdate)
        self.response.out.write('Schema migration successfully initiated.')
