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
import logging
import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import webapp

# constants

MAX_BLOB_LIFESPAN_DAYS = 5


# handlers

class BlobstoreDeleteHandler(webapp.RequestHandler):
    def get(self):
        query = blobstore.BlobInfo.all()
        blobs = query.fetch(10000)
        deletion_count = 0
        for blob in blobs:
            age = datetime.datetime.utcnow() - blob.creation

            # delete CSV blobs
            if blob.filename.endswith('.csv') and age.days >= MAX_BLOB_LIFESPAN_DAYS:
                blob.delete()
                deletion_count += 1

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Deleted %d blob(s) from blobstore.' % deletion_count)

