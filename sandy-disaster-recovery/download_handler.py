
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers

import base
from time_utils import timestamp
from export_bulk_handler import all_event_timeless_filename


class DownloadBulkExportHandler(
        base.AuthenticatedHandler,
        blobstore_handlers.BlobstoreDownloadHandler):

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

        # find blob
        blob_infos = BlobInfo.all().filter('filename', filename).order('-creation')

        if blob_infos.count() == 0:
            # say not ready yet (HTTP 202)
            self.response.set_status(202)
        else:
            # send the blob as a file, forcing download
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
