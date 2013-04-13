import logging
import organization
from google.appengine.ext import deferred
from google.appengine.ext import db
import site_db

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(self, event, cursor=None, num_updated=0): 
    query = site_db.Site.all()
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE):
        to_put.append(p)

    if to_put:
        db.put(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
        self.redirect('/admin?message=Update Schema Completed Successfully')     
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)