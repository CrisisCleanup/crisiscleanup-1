import webapp2
import update_sites_handler
from google.appengine.ext import deferred

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(update_sites_handler.UpdateSchema)
        self.response.out.write('Schema migration successfully initiated.')
