import logging
import organization
from google.appengine.ext import deferred
from google.appengine.ext import db
import random
import site_db
import event_db

BATCH_SIZE = 10  # ideal batch size may vary based on entity size.

def UpdateSchema(self, event, cursor=None, num_updated=0): 
    logging.debug("UpdateSchema")
    OFFSET_SIZE = int(num_updated) * BATCH_SIZE
    logging.debug(OFFSET_SIZE)
    query = site_db.Site.all()
    
    other_q = event_db.Event.all()
    other_q.filter("short_name =", "moore")
    moore_event = other_q.get()
    query.filter("event =", moore_event.key())
    logging.debug(moore_event.name)
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE, offset = OFFSET_SIZE):
        p.blurred_latitude = p.latitude + random.uniform(-0.001798, 0.001798)
	p.blurred_longitude = p.longitude + random.uniform(-0.001798, 0.001798)
	#raise Exception(p)
        # In this example, the default values of 0 for num_votes and avg_rating
        # are acceptable, so we don't need this loop.  If we wanted to manually
        # manipulate property values, it might go something like this:
        #p.org_verified = True
        #p.is_active = True
        #p.address="n/a"
        #p.city="n/a"
        #p.state="n/a"
        #p.zip_code="n/a"
        
        #p.url="n/a"
        #p.twitter="n/a"
        #p.facebook="n/a"
        #p.email="n/a"
        #p.incident=event.key()
        #p.physical_presence=True
        #p.work_area="n/a"
        #p.number_volunteers="n/a"
        #p.voad_member=True
        #p.voad_member_url="n/a"
        #p.voad_referral="n/a"
        #p.canvass = True
        #p.assessments = True
        #p.clean_up = True
        #p.mold_abatement = True
        #p.rebuilding=True
        #p.refurbishing=True
        #p.is_admin=False
        to_put.append(p)

    if to_put:
        db.put(to_put)
        #num_updated += len(to_put)
        #logging.debug(
            #'Put %d entities to Datastore for a total of %d',
            #len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)

        if len(to_put) == BATCH_SIZE and num_updated != 18:
	  next_update = int(num_updated) + 1
	  logging.debug(next_update)
	  self.redirect("/update_handler?num_updates=" + str(next_update))
	else:
	  self.redirect('/admin?message=Update Schema Completed Successfully')     
    else:
        logging.debug(
            'UpdateSchema complete with updates')