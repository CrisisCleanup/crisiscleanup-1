import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
import site_db
import event_db

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        raise Exception(blob_info)
        process_csv(blob_info)

        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")


def process_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter=';')
    for row in reader:
        date, data, value = row
        entry = EntriesDB(date=date, data=data, value=int(value))
        entry.put()
