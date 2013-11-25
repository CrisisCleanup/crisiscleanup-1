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

from google.appengine.api import urlfetch
import json

import api_key_db
from memoize import memoize


_VOTESMART_API_KEY = None


def get_api_key():
    global _VOTESMART_API_KEY
    if _VOTESMART_API_KEY is None:
        _VOTESMART_API_KEY = api_key_db.get_api_key('votesmart')
    return _VOTESMART_API_KEY


def construct_url(function_name, params):
    key = get_api_key()
    return "http://api.votesmart.org/%s?o=JSON&key=%s&" % (function_name, key) + (
        "&".join(
            '%s=%s' % (k,v) for k,v in params.items()
        )
    )


def request(url):
    " Request using GAE library. "
    r = urlfetch.fetch(url)
    if r.status_code != 200:
        raise Exception(r.code)
    return json.loads(r.content)


@memoize(1000)
def officials_by_zip(zip_code):
    url = construct_url('Officials.getByZip', {'zip5': zip_code})
    d = request(url)

    candidates = d.get('candidateList', {}).get('candidate', [])
    return candidates


@memoize(1000)
def candidate_addresses(candidate_id):
    " Return dictionary of office and web addresses for candidate with id. "
    addresses = {
        'offices': [],
        'web_addresses': [],
    }

    # get office addresses and phone numbers
    url = construct_url('Address.getOffice', {'candidateId': candidate_id})
    d = request(url)
    offices = d.get('address', {}).get('office', [])
    if type(offices) is not list:
        offices = [offices]
    addresses['offices'] = offices

    # get web addresses
    url = construct_url('Address.getOfficeWebAddress', {'candidateId': candidate_id})
    d = request(url)
    web_addresses = d.get('webaddress', {}).get('address', [])
    if type(web_addresses) is not list:
        web_addresses = [web_addresses]
    addresses['web_addresses'] = web_addresses

    return addresses


def augment_candidate_with_addresses(candidate):
    " Augment candidate dict with office and web addresses. "
    candidate_id = candidate['candidateId']
    candidate.update(candidate_addresses(candidate_id))
    return candidate


def officials_with_addresses_by_zip(zip_code):
    candidates = officials_by_zip(zip_code)
    map(augment_candidate_with_addresses, candidates)
    return candidates
