import logging
import organization
from google.appengine.ext import deferred
from google.appengine.ext import db

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(self, event, cursor=None, num_updated=0): 
    query = organization.Organization.all()
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE):
        # In this example, the default values of 0 for num_votes and avg_rating
        # are acceptable, so we don't need this loop.  If we wanted to manually
        # manipulate property values, it might go something like this:
        p.org_verified = True
        p.is_active = True
        p.address="n/a"
        p.city="n/a"
        p.state="n/a"
        p.zip_code="n/a"
        
        p.url="n/a"
        p.twitter="n/a"
        p.facebook="n/a"
        p.email="n/a"
        p.incident=event.key()
        p.physical_presence=True
        p.work_area="n/a"
        p.number_volunteers="n/a"
        p.voad_membership=True
        p.voad_membership_url="n/a"
        p.voad_referral="n/a"
        p.canvassing = True
        p.assessments = True
        p.clean_up = True
        p.mold_abatement = True
        p.rebuilding=True
        p.refurbishing=True
        p.is_admin=False
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