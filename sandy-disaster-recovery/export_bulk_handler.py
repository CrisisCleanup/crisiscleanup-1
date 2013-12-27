
import datetime
import re
import json
import csv
from StringIO import StringIO

from google.appengine.api import taskqueue
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo, BlobReader
from google.appengine.ext.webapp import blobstore_handlers

import webapp2

import base
from site_db import Site
from event_db import Event
from time_utils import timestamp, timestamp_now
from cron_utils import AbstractCronHandler


# constants

DEFAULT_SITES_PER_TASK = 20

DEFAULT_CSV_FIELDS_LIST = ["claimed_by", "reported_by", "modified_by", "case_number", "Days Waiting From %(today)s", "name", "request_date", "address", "city", "county", "state", "zip_code", "latitude", "longitude", "blurred_latitude", "blurred_longitude","cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_assessing_organization", "first_responder", "older_than_60", "disabled", "priority", "flood_height", "floors_affected", "carpet_removal", "hardwood_floor_removal", "drywall_removal", "heavy_item_removal", "appliance_removal", "standing_water", "mold_remediation", "pump_needed", "num_trees_down", "num_wide_trees", "roof_damage", "tarps_needed", "debris_removal_only", "habitable", "electricity", "electrical_lines", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "prepared_by", "do_not_work_before", "special_needs", "work_requested", "notes"]

MOORE_CSV_FIELDS_LIST = ["claimed_by", "reported_by", "modified_by", "case_number", "Days Waiting From %(today)s", "name","request_date","address","city","county","state","zip_code", "latitude", "longitude", "blurred_latitude", "blurred_longitude", "cross_street","phone1","phone2","time_to_call","work_type","house_affected","outbuilding_affected","exterior_property_affected","rent_or_own","work_without_resident","member_of_assessing_organization","first_responder","older_than_60","special_needs","priority","destruction_level","house_roof_damage","outbuilding_roof_damage","tarps_needed","help_install_tarp","num_trees_down","num_wide_trees","interior_debris_removal","nonvegitative_debris_removal","vegitative_debris_removal","unsalvageable_structure","heavy_machinary_required","damaged_fence_length","fence_type","fence_notes","notes","habitable","electricity","electrical_lines","unsafe_roof","unrestrained_animals","other_hazards","status","assigned_to","total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present","status_notes","prepared_by","do_not_work_before"]

PULASKI_CSV_FIELDS_LIST = ["claimed_by", "reported_by", "modified_by", "case_number", "Days Waiting From %(today)s", "name", "request_date", "address", "city", "county", "state", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_assessing_organization", "first_responder", "older_than_60", "special_needs", "priority", "flood_height", "floors_affected", "carpet_removal", "hardwood_floor_removal", "drywall_removal", "appliance_removal", "heavy_item_removal", "standing_water", "mold_remediation", "pump_needed", "work_requested", "notes", "nonvegitative_debris_removal", "vegitative_debris_removal", "house_roof_damage", "outbuilding_roof_damage", "tarps_needed", "help_install_tarp", "num_trees_down", "num_wide_trees", "habitable", "electricity", "electrical_lines", "unsafe_roof", "flammables", "other_hazards", "rebuild", "num_stories", "num_rooms", "occupied", "dwelling_type", "residency", "air_conditioning_type", "heat_type", "gas_source", "gas_status", "gas_shutoff_location", "water_source", "water_status", "water_shutoff_location", "septic_type", "septic_location", "damage_overall", "damage_electrical", "damage_gas", "damage_septic", "damage_wells", "damage_fencing", "damage_concrete", "damage_yard", "damage_shingles", "damage_roof_metal", "damage_roof_tile", "damage_foundation", "damage_brick_wall", "damage_siding", "damage_cmu", "damage_windows", "damage_doors", "exterior_notes", "damage_drywall", "damage_plaster_walls", "damage_paneling", "damage_hardwood_floor", "damage_carpet", "damage_ceiling", "damage_kitchen", "damage_bathroom", "damage_refrigerator", "damage_stove", "interior_notes", "damage_furnace", "damage_ac", "damage_ducts", "hvac_notes", "status", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "status_notes", "prepared_by", "do_not_work_before", "cost_estimate_total", "cost_estimate_notes"]


# functions

def get_csv_fields_list(event_short_name):
    " Return CSV fields list with substitutions interpolated. "
    # choose fields list
    if event_short_name in ('moore', 'midwest_tornadoes'):
        csv_fields_list = MOORE_CSV_FIELDS_LIST
    elif event_short_name == 'pulaski':
        csv_fields_list = PULASKI_CSV_FIELDS_LIST
    else:
        csv_fields_list = DEFAULT_CSV_FIELDS_LIST

    # apply substitutions
    subs = {
        'today': str(datetime.date.today()),
    }
    return [field % subs for field in csv_fields_list]


class AbstractExportBulkHandler(object):

    def get_continuation_param_dict(self):
        return {
            'cursor': '',
            'event': self.filtering_event_key,
            'filename': self.filename,
            'blobstore_filename': self.blobstore_filename,
            'csv_header': self.csv_header,
            'worker_url': self.worker_url,
        }

    def start_export(self, org, event, worker_url, filtering_event_key=None, filename=None):
        self.worker_url = worker_url

        # create filename if not supplied
        if filename is None:
            filename = "%s-%s-%s.csv" % (
                re.sub(r'\W+', '-', event.name.lower()),
                re.sub(r'\W+', '-', org.name.lower()),
                timestamp_now(),
            )
        self.filename = filename

        # create file in blobstore
        self.blobstore_filename = files.blobstore.create(
            mime_type='text/csv',
           _blobinfo_uploaded_filename=filename
        )

        # decide header/title row
        header_sio = StringIO()
        writer = csv.writer(header_sio)
        writer.writerow([
            "%s Work Orders. Created %s UTC%s" % (
                event.name,
                str(datetime.datetime.utcnow()).split('.')[0],
                ' by %s' % org.name if org else ''
            )
        ])
        writer.writerow(
            get_csv_fields_list(event.short_name)
        )
        self.csv_header = header_sio.getvalue()
        header_sio.close()

        # select event filter based on parameter or org-user
        if filtering_event_key:
            self.filtering_event_key = filtering_event_key
        elif org.is_global_admin:
            self.filtering_event_key = ''
        else:
            self.filtering_event_key = event.key()

        # start first task
        taskqueue.add(
            url=self.worker_url,
            params=self.get_continuation_param_dict(),
        )

        # write filename out as json
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            json.dumps({
                'filename': filename
            })
        )


class ExportBulkHandler(base.AuthenticatedHandler, AbstractExportBulkHandler):

    def AuthenticatedGet(self, org, event):
        self.handle(org, event)

    def AuthenticatedPost(self, org, event):
        self.handle(org, event)

    def handle(self, org, event):
        if self.request.get('download') == 'selected':
            self.id_list = self.request.get('id_list')
        else:
            self.id_list = []

        # start export, forcing filter to current event
        self.start_export(
            org,
            event,
            '/export_bulk_worker',
            filtering_event_key=event.key()
        )

    def get_continuation_param_dict(self):
        d = super(ExportBulkHandler, self).get_continuation_param_dict()
        d['id_list'] = self.id_list
        return d


def all_event_timeless_filename(event):
    return "%s-ALL.csv" % re.sub(r'\W+', '-', event.name.lower())


class ExportAllEventsHandler(AbstractCronHandler, AbstractExportBulkHandler):

    def get(self):
        # start export Task chain for each event
        for event in Event.all():
            filename = all_event_timeless_filename(event)
            self.start_export(
                org=None,
                event=event,
                worker_url='/export_bulk_worker',
                filtering_event_key=event.key(),
                filename=filename,
            )


class AbstractExportBulkWorker(webapp2.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(AbstractExportBulkWorker, self).__init__(*args, **kwargs)
        self.event = None
        self.sites_per_task = DEFAULT_SITES_PER_TASK

    def _write_csv_rows(self, fd, sites):
        writer = csv.writer(fd)
        event_short_name = self.event.short_name if self.event else None
        fields = get_csv_fields_list(event_short_name)
        for site in sites:
            writer.writerow(site.ToCsvLine(fields))

    def get_base_query(self):
        raise NotImplementedError

    def filter_sites(self):
        raise NotImplementedError

    def get_continuation_param_dict(self):
        return {
            'cursor': self.end_cursor,
            'event': self.filtering_event_key,
            'filename': self.filename,
            'blobstore_filename': self.blobstore_filename,
            'csv_header': self.csv_header,
            'worker_url': self.worker_url,
        }

    def post(self):
        # get args
        self.start_cursor = self.request.get('cursor')
        self.filtering_event_key = self.request.get('event')
        self.filename = self.request.get('filename')
        self.blobstore_filename = self.request.get('blobstore_filename')
        self.csv_header = self.request.get('csv_header')
        self.worker_url = self.request.get('worker_url')

        self.event = Event.get(self.filtering_event_key) if self.filtering_event_key else None

        # get (base) query, skip query to cursor, filter for sites
        query = self.get_base_query()
        if self.start_cursor:
            query.with_cursor(self.start_cursor)
        fetched_sites = query.fetch(limit=self.sites_per_task)
        sites = self.filter_sites(fetched_sites)

        # write lines to blob file
        with files.open(self.blobstore_filename, 'a') as fd:
            self._write_csv_rows(fd, sites)

        # decide what to do next
        self.end_cursor = query.cursor()
        if self.end_cursor and self.start_cursor != self.end_cursor:
            # chain to next task
            taskqueue.add(
                url=self.worker_url,
                params=self.get_continuation_param_dict()
            )
        else:
            # finish file: deduplicate lines
            files.finalize(self.blobstore_filename)
            generated_file_blob_key = files.blobstore.get_blob_key(
                self.blobstore_filename)
            blob_reader = BlobReader(generated_file_blob_key)
            deduplicated_lines = set(line for line in blob_reader)
            blobstore.delete(generated_file_blob_key)

            # write csv header and deduplicated lines to new file
            deduplicated_blobstore_filename = files.blobstore.create(
                mime_type='text/csv',
               _blobinfo_uploaded_filename=self.filename
            )
            with files.open(deduplicated_blobstore_filename, 'a') as fd:
                fd.write(self.csv_header)
                for line in deduplicated_lines:
                    fd.write(line)
            files.finalize(deduplicated_blobstore_filename)


class ExportBulkWorker(AbstractExportBulkWorker):

    " Used by front-end map. "

    def __init__(self, *args, **kwargs):
        super(ExportBulkWorker, self).__init__(*args, **kwargs)
        self.sites_per_task = 200  # override
    
    def post(self):
        self.id_list = self.request.get('id_list')
        self.ids = (
            set(int(x) for x in self.id_list.split(','))
            if self.id_list else set()
        )
        super(ExportBulkWorker, self).post()

    def get_base_query(self):
        query = Site.all()
        if self.filtering_event_key:
            query.filter('event', Event.get(self.filtering_event_key))
        return query

    def filter_sites(self, fetched_sites):
        # filter on ids if supplied
        # (GAE: can't do as part of query with cursor...)
        if self.ids:
            return [
                site for site in fetched_sites
                if site.key().id() in self.ids
            ]
        else:
            return fetched_sites

    def get_continuation_param_dict(self):
        d = super(ExportBulkWorker, self).get_continuation_param_dict()
        d['id_list'] = self.id_list
        return d


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


class DownloadEventAllWorkOrdersHandler(
        base.AuthenticatedHandler,
        blobstore_handlers.BlobstoreDownloadHandler):

    def AuthenticatedGet(self, org, event):
        # retrieve most recent blob with filename of event
        filename = all_event_timeless_filename(event)
        blob_infos = BlobInfo.all().filter('filename', filename).order('-creation')
        if blob_infos.count() == 0:
            self.abort(404)

        # rewrite filename to include timestamp
        blob_info_to_serve = blob_infos[0]
        filename_to_serve = blob_info_to_serve.filename.replace(
            '.csv',
            '-%s.csv' % timestamp(blob_info_to_serve.creation)
        )

        # serve the blob as an attachment
        self.response.headers['Content-Disposition'] = (
            str('attachment; filename="%s"' % filename_to_serve)
        )
        self.send_blob(blob_info_to_serve)
