import webapp2
import add_permissions_schema_update
from google.appengine.ext import deferred
import organization

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        # deferred.defer(add_permissions_schema_update.AddPermissionsSchemaUpdate)
        # self.response.out.write('Schema migration successfully initiated.')
        orgs = organization.Organization.all()
        for org in orgs:
        	password_hash = org.password
        	org._password_hash_list.append(password_hash)
        	org.password = ""
        	organization.PutAndCache(org)
        # log. Save old?
        self.response.out.write('Passwords updated')