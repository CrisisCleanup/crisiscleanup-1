
import datetime

from google.appengine.api import app_identity
import cloudstorage

import base
from time_utils import timestamp
from export_bulk_handler import all_event_timeless_filename

import incident_permissions_db


# constants

APP_ID = app_identity.get_application_id()
BUCKET_NAME = '/' + APP_ID


# classes

class DownloadBulkExportHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        filename = self.request.get('filename')
        if not filename:
            self.abort(404)

        # check we are allowed to get this file, by filename
        allowed_filename_substrs = [inc.filename_friendly_name for inc in org.incidents]
        allowed_to_access = (
            org.is_global_admin or
            any(s in filename for s in allowed_filename_substrs)
        )
        if not allowed_to_access:
            self.abort(403)

        # find file in GCS
        bucket_path = BUCKET_NAME + '/' + filename
        try:
            file_stat = cloudstorage.stat(bucket_path)
        except cloudstorage.NotFoundError:
            # say not ready yet (HTTP 202)
            self.response.set_status(202)
            return

        # send the file contents & force download
        gcs_fd = cloudstorage.open(bucket_path)
        if file_stat.content_type:
            self.response.headers['Content-Type'] = file_stat.content_type
        self.response.headers['Content-Disposition'] = (
            str('attachment; filename="%s"' % filename)
        )
        self.response.write(gcs_fd.read())


class DownloadEventAllWorkOrdersHandler(base.AuthenticatedHandler):

    def AuthenticatedGet(self, org, event):
        filename = all_event_timeless_filename(event)
        bucket_path = BUCKET_NAME + '/' + filename

        try:
            file_stat = cloudstorage.stat(bucket_path)
        except cloudstorage.NotFoundError:
            self.abort(404)

        # rewrite filename to include timestamp
        custom_timestamp = timestamp(
            datetime.datetime.utcfromtimestamp(file_stat.st_ctime))
        filename_to_serve = file_stat.filename.replace(
            '.csv',
            '-%s.csv' % custom_timestamp 
        )

        # serve the file as an attachment, forcing download
        gcs_fd = cloudstorage.open(bucket_path)
        if file_stat.content_type:
            self.response.headers['Content-Type'] = file_stat.content_type
        self.response.headers['Content-Disposition'] = (
            str('attachment; filename="%s"' % filename_to_serve)
        )
	
        if org.permissions == "Situational Awareness":
	  i_ps = incident_permissions_db.IncidentPermissions.all()
	  i_ps.filter("incident =", event.key())
	  this_i_ps = i_ps.get()
	  delete = this_i_ps.situational_awareness_redactions
	  i = 0
	  for r in gcs_fd.read():
	    i = i + 1
	    if r == "name":
	      raise Exception(i)
	    else:
	      raise Exception("none found")
	  raise Exception("didn't loop")
	    
	  
	  
	  
	else:
	  self.response.write(gcs_fd.read())



def remove_csv_columns(csv_file, column_numbers):
  for number in column_numbers:
    pass


def get_csv_column_numbers(csv_file, column_names):
  column_numbers = []
  
  
  return column_numbers