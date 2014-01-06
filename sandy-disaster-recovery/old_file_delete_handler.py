#!/usr/bin/env python
#
# Copyright 2013 Chris Wood
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime

from google.appengine.ext import blobstore
from google.appengine.api import app_identity
import cloudstorage

from cron_utils import AbstractCronHandler


# constants

APP_ID = app_identity.get_application_id()
BUCKET_NAME = '/' + APP_ID

MAX_FILE_LIFESPAN_DAYS = 14


# handler

class OldFileDeleteHandler(AbstractCronHandler):

    def get(self):
        # delete blobs
        query = blobstore.BlobInfo.all()
        blobs = query.fetch(10000)
        blob_deletion_count = 0

        for blob in blobs:
            age = datetime.datetime.utcnow() - blob.creation

            # delete CSV & HTML blobs
            should_delete = (
                blob.filename is not None 
                and (blob.filename.endswith('.csv') or blob.filename.endswith('.html'))
                and age.days > MAX_FILE_LIFESPAN_DAYS
            )
            if should_delete:
                blob.delete()
                blob_deletion_count += 1

        # delete from GCS
        gcs_deletion_count = 0
        for file_stat in cloudstorage.listbucket(BUCKET_NAME):
            age = datetime.datetime.utcnow() - \
                datetime.datetime.utcfromtimestamp(file_stat.st_ctime)
            should_delete = (
                ('.csv' in file_stat.filename or '.html' in file_stat.filename)
                and age.days > MAX_FILE_LIFESPAN_DAYS
            )
            if should_delete:
                cloudstorage.delete(file_stat.filename)
                gcs_deletion_count += 1

        # write outcome
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Deleted %d blobs from blobstore.\n' % blob_deletion_count)
        self.response.out.write('Deleted %d files from GCS.\n' % gcs_deletion_count)

