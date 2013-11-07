
import time
import datetime
import re
import json
import csv

from google.appengine.api import taskqueue
from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers

import webapp2

import base
from site_db import Site
from event_db import Event


# constants

SITES_PER_TASK = 100

CSV_FIELDS_LIST = ["claimed_by", "reported_by", "modified_by", "case_number", "Days Waiting From %(today)s", "name", "request_date", "address", "city", "county", "state", "zip_code", "latitude", "longitude", "blurred_latitude", "blurred_longitude","cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_assessing_organization", "first_responder", "older_than_60", "disabled", "priority", "flood_height", "floors_affected", "carpet_removal", "hardwood_floor_removal", "drywall_removal", "heavy_item_removal", "appliance_removal", "standing_water", "mold_remediation", "pump_needed", "num_trees_down", "num_wide_trees", "roof_damage", "tarps_needed", "debris_removal_only", "habitable", "electricity", "electrical_lines", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "prepared_by", "do_not_work_before", "special_needs", "work_requested", "notes"]


# functions

def get_csv_fields_list():
    " Return CSV fields list with substitutions interpolated. "
    subs = {
        'today': str(datetime.date.today()),
    }
    return [field % subs for field in CSV_FIELDS_LIST]


class ExportBulkHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        self.handle(org, event)

    def AuthenticatedPost(self, org, event):
        self.handle(org, event)

    def handle(self, org, event):
        if self.request.get('download') == 'selected':
            id_list = self.request.get('id_list')
        else:
            id_list = []
        self.start_export(org, event, id_list)

    def start_export(self, org, event, id_list):
        # create filename
        filename = "%s-%s-%s.csv" % (
            re.sub(r'\W+', '-', event.name.lower()),
            re.sub(r'\W+', '-', org.name.lower()),
            str(time.time())
        )

        # create file in blobstore
        blobstore_filename = files.blobstore.create(
            mime_type='text/csv',
           _blobinfo_uploaded_filename=filename
        )

        # write header/title row
        with files.open(blobstore_filename, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow([
                "%s Work Orders. Downloaded %s UTC by %s" % (
                    event.name,
                    str(datetime.datetime.utcnow()).split('.')[0],
                    org.name
                )
            ])
            writer.writerow(get_csv_fields_list())

        # start first task
        taskqueue.add(
            url='/export_bulk_worker',
            params={
                'cursor': '',
                'event': event.key(),
                'filename': blobstore_filename,
                'id_list': id_list,
            }
        )

        # write json
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            json.dumps({
                'filename': filename
            })
        )


class ExportBulkWorker(webapp2.RequestHandler):

    def _write_csv_rows(self, fd, sites):
        writer = csv.writer(fd)
        fields = get_csv_fields_list()
        for site in sites:
            writer.writerow(site.ToCsvLine(fields))

    def post(self):
        # get args
        start_cursor = self.request.get('cursor')
        event = Event.get(self.request.get('event'))
        filename = self.request.get('filename')
        id_list = self.request.get('id_list')
        ids = (
            set(int(x) for x in id_list.split(','))
            if id_list else set()
        )

        # construct query
        query = Site.all().filter('event', event)
        if start_cursor:
            query.with_cursor(start_cursor)
        sites = query.fetch(limit=SITES_PER_TASK)

        # filter on ids if supplied
        # (GAE: can't do as part of query with cursor...)
        if ids:
            sites = [site for site in sites if site.key().id() in ids]

        # write lines to blob file
        with files.open(filename, 'a') as fd:
            self._write_csv_rows(fd, sites)

        # decide what to do next
        end_cursor = query.cursor()
        if end_cursor and start_cursor != end_cursor:
            # chain to next task
            taskqueue.add(
                url='/export_bulk_worker',
                params={
                    'cursor': end_cursor,
                    'event': event.key(),
                    'filename': filename,
                    'id_list': id_list,
                }
            )
        else:
            # finalize
            files.finalize(filename)


class DownloadBulkExportHandler(
        base.AuthenticatedHandler,
        blobstore_handlers.BlobstoreDownloadHandler):

    def AuthenticatedGet(self, org, event):
        filename = self.request.get('filename')
        if not filename:
            webapp2.abort(404)

        blob_infos = BlobInfo.all().filter('filename', filename).order('-creation')

        if blob_infos.count() == 0:
            # say not ready yet (HTTP 202)
            self.response.set_status(202)
        else:
            # send the blob as a file
            blob_info = blob_infos[0]
            self.response.headers['Content-Disposition'] = (
                str('attachment; filename="%s"' % filename)
            )
            self.send_blob(blob_info)
