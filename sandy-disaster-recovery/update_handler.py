import webapp2
import add_permissions_schema_update
import update_sites_handler
from google.appengine.ext import deferred

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(add_permissions_schema_update.AddPermissionsSchemaUpdate)
        self.response.out.write('Schema migration successfully initiated.')
        deferred.defer(update_sites_handler.UpdateSchema)
        self.response.out.write('Schema migration successfully initiated.')
