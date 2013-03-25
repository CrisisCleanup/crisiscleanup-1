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

from google.appengine.ext import deferred
from google.appengine.api import search

import base
import site_db


# constants

GLOBAL_ADMIN_NAME = "Admin"


# handler

class ScriptsHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        # require global admin
        if org.name != GLOBAL_ADMIN_NAME:
            self.redirect("/")
            return

        # choose script
        ran_script = True
        script_name = self.request.get('script', None)
        if script_name == 'compute_all_sims':
            offset = int(self.request.get('offset', 0))
            compute_all_sims(offset)
        elif script_name == 'insert_all_geosearch_docs':
            offset = int(self.request.get('offset', 0))
            insert_all_geosearch_docs(offset)
        else:
            ran_script = False

        # write output
        self.response.headers['Content-Type'] = 'text/plain'
        if ran_script:
            self.response.out.write('Ran %s successfully' % script_name)
        else:
            self.response.out.write('Unknown script name: "%s"' % script_name)

# scripts

def compute_all_sims(offset):
    for i, site in enumerate(site_db.Site.all().run(offset=offset)):
        if site.name and not site.name_metaphone:
            site.compute_similarity_matching_fields()
            logging.info(site.name_metaphone)
            site.put()
        else:
            logging.info("skipping %s..." % i)

def _geoindex_doc(site_key):
    site = site_db.Site.get(site_key)
    search_doc = search.Document(
        doc_id=str(site.key()),
        fields=[
          search.GeoField(name='loc', value=search.GeoPoint(site.latitude, site.longitude))
    ])
    search.Index(name='GEOSEARCH_INDEX').put(search_doc)

def insert_all_geosearch_docs(offset):
    logging.info('Deferring geoindexing of all sites (offset=%s)...' % offset)
    for i, site in enumerate(site_db.Site.all().run(offset=offset)):
        deferred.defer(_geoindex_doc, site.key())
        logging.warn('deferred %s' %i)
    logging.info('Finish defers')
        
