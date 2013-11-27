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

from google.appengine.ext import db

from unicode_csv import UnicodeDictReader


class ZipCode(db.Expando):
    " GAE key name is also the zip "
    zip = db.StringProperty(required=True)



def load_zip_code_csv(path):
    UNWANTED_FIELDS = {
        'acceptable_cities',
        'unacceptable_cities',
    }
    BATCH_SIZE = 200
    with open(path) as fd:
        reader = UnicodeDictReader(fd)
        queue = []
        for i, row_d in enumerate(reader):
            key_name = row_d['zip']
            for field in UNWANTED_FIELDS:
                del(row_d[field])
            zc = ZipCode(key_name=key_name, **row_d)
            queue.append(zc)
            if i and i % BATCH_SIZE == 0:
                # bulk insert
                db.put(queue)
                queue = []
                print i
        db.put(queue)
