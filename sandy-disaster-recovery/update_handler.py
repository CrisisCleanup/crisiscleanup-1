import webapp2
import add_permissions_schema_update
from google.appengine.ext import deferred
import organization
import generate_hash

class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        # deferred.defer(add_permissions_schema_update.AddPermissionsSchemaUpdate)
        # self.response.out.write('Schema migration successfully initiated.')
        orgs = organization.Organization.all()
        for org in orgs:
        	org._password_hash_list.append(generate_hash.recursive_hash(org.password))
        	# org.password = ""
            org._password_hash_list = org._password_hash_list(list(set(org._password_hash_list)))
        	organization.PutAndCache(org)
        # log. Save old?
        self.response.out.write('Passwords updated')