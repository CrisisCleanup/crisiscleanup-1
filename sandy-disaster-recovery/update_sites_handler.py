import logging
import models
from google.appengine.ext import deferred
from google.appengine.ext import db

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

import site_db

def UpdateSchema(cursor=None, num_updated=0):
    query = site_db.Site.all()

    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE):
        # In this example, the default values of 0 for num_votes and avg_rating
        # are acceptable, so we don't need this loop.  If we wanted to manually
        # manipulate property values, it might go something like this:
        p.is_legacy_and_first_phase = True
        to_put.append(p)
        logging.debug("end loop")

    if to_put:
        db.put(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)
    finish()
    raise Exception("done")
