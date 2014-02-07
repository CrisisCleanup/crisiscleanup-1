import webapp2
import add_phases_schema_update
from google.appengine.ext import deferred

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(add_phases_schema_update.AddPhasesSchemaUpdate)
        self.response.out.write('Schema migration successfully initiated.')
