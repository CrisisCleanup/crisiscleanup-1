#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
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
# System libraries.
import datetime
import logging
import re
import random

from wtforms.ext.appengine.db import model_form

from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import Query
from google.appengine.api import search
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField

# Local libraries.
import event_db
import organization
import metaphone

STANDARD_SITE_PROPERTIES_LIST = ['name', 'case_number', 'event', 'reported_by', 'claimed_by', 
				'address', 'city', 'state', 'county', 'zip_code', 'cross_street', 'landmark', 
				'phone1', 'phone2', 'name_metaphone', 'address_digits', 'address_metaphone',
				'city_metaphone', 'phone_normalised', 'latitude', 'longitude',
				'work_type', 'priority']

PERSONAL_INFORMATION_MODULE_ATTRIBUTES = ["name", "request_date", "address", "city", "state", "county", "zip_code", "latitude", "longitude", "cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_organization", "first_responder", "older_than_60", "disabled", "special_needs", "priority"]

def _GetOrganizationName(site, field):
  """Returns the name of the organization in the given field, if possible.
  """
  if hasattr(site, field):
    try:
      org = getattr(site, field)
    except db.ReferencePropertyResolveError:
      return None
    if org:
      return org.name
    return None

def _GetField(site, field):
  """Simple field accessor, with a bit of logging."""
  try:
    return getattr(site, field)
  except AttributeError:
    logging.warn('site %s is missing attribute %s' % (site.key().id(), field))
    return None


STATUSES = [
  "Open, unassigned",
  "Open, assigned",
  "Open, partially completed",
  "Open, needs follow-up",
  "Closed, completed",
  "Closed, incomplete",
  "Closed, out of scope",
  "Closed, done by others",
  "Closed, no help wanted",
  "Closed, rejected",
  "Closed, duplicate",
]

STATUSES_UNICODE = map(unicode, STATUSES)


class Site(db.Expando):
  # The list of fields that will be included in the CSV output.
  CSV_FIELDS = []

  # Data about the site itself.
  name = db.StringProperty(required = True)
  case_number = db.StringProperty()
  event = db.ReferenceProperty(event_db.Event)
  #reported_by = db.ReferenceProperty(organization.Organization,
                                     #collection_name="reported_site_set")
  request_date = db.DateTimeProperty(auto_now_add=True)
  address = db.StringProperty(required = True)
  city = db.StringProperty()
  county = db.StringProperty()
  state = db.StringProperty()
  zip_code = db.StringProperty()
  cross_street = db.StringProperty()
  landmark = db.StringProperty()
  phone1 = db.StringProperty()
  phone2 = db.StringProperty()

  # similarity-matching fields
  name_metaphone = db.StringProperty()
  address_digits = db.StringProperty()
  address_metaphone = db.StringProperty()
  city_metaphone = db.StringProperty()
  phone_normalised = db.StringProperty()


  #work_type = db.StringProperty()
  latitude = db.FloatProperty(default = 0.0)
  longitude = db.FloatProperty(default = 0.0)
  status = db.StringProperty(
    choices=STATUSES,
    default="Open, unassigned"
  )
  
  open_phases_list = db.StringListProperty()

  def get_phase_field(self, phase_name, field_name):
      combined_field_name = u'phase_%s_%s' %(phase_name, field_name)
      return getattr(self, combined_field_name)

  def get_primary_phase_field(self, field_name):
      primary_phase_name = self.open_phases_list[0]
      return self.get_phase_field(primary_phase_name, field_name)

  @property
  def county_and_state(self):
      return (
          (self.county if self.county else u'[Unknown]') +
          ((u', %s' % self.state) if self.state else u'')
      )

  @property
  def full_address(self):
    return ", ".join(
      map(
        lambda field: field if field else '',
        [self.address, self.city, self.county, self.state, self.zip_code]
      )
    )

  def put(self, **kwargs):
      " On-save "
      # set blurred co-ordinates
      self.blurred_latitude = self.latitude + random.uniform(-0.001798, 0.001798)
      self.blurred_longitude = self.longitude + random.uniform(-0.001798, 0.001798)
      super(Site, self).put(**kwargs)


  _CSV_ACCESSORS = {
    'reported_by': _GetOrganizationName,
    'claimed_by': _GetOrganizationName,
    }

  def compute_similarity_matching_fields(self):
    """Use double metaphone values and store as 'X-Y'."""
    self.name_metaphone = '%s-%s' % metaphone.dm(unicode(self.name)) if self.name else None
    self.address_digits = _filter_non_digits(self.address) if self.address else None
    self.address_metaphone = '%s-%s' % metaphone.dm(unicode(self.address)) if self.address else None
    self.city_metaphone = '%s-%s' % metaphone.dm(unicode(self.city)) if self.city else None
    self.phone_normalised = _filter_non_digits(self.phone1) if self.phone1 else None

  def similar(self, event):
    """Find a single similar site in @event using find_similar()."""
    self.compute_similarity_matching_fields()
    return find_similar(self, event)

  def ToCsvLine(self, extra_csv_list):
    """
    Returns the site as a list of string values, one per field in
    CSV_FIELDS.
    """
    csv_row = []
    fields_list = extra_csv_list
    for field in fields_list:
      # get value using looked-up accessor function
      accessor = self._CSV_ACCESSORS.get(field, _GetField)
      value = accessor(self, field)

      # append value to row, handling special cases first
      if field.startswith('Days Waiting From'):
        csv_row.append(
            (datetime.datetime.utcnow() - self.request_date).days
        )
      elif value is None:
        csv_row.append('')
      else:
        try:
          csv_row.append(unicode(value).encode("utf-8"))
        except:
          logging.critical("Failed to parse: " + value + " " + str(self.key().id()))
    return csv_row


APARTMENT_SIGNIFIERS = ["#", "Suite", "Ste", "Apartment", "Apt", "Unit", "Department", "Dept", "Room", "Rm", "Floor", "Fl", "Bldg", "Building", "Basement", "Bsmt", "Front", "Frnt", "Lobby", "Lbby", "Lot", "Lower", "Lowr", "Office", "Ofc", "Penthouse", "Pent", "PH", "Rear", "Side", "Slip", "Space", "Trailer", "Trlr", "Upper", "Uppr"]

APARTMENT_TERM_CRX = re.compile(
    "(" + "|".join(("%s[^W]+\s" % s for s in APARTMENT_SIGNIFIERS)) + ")", re.I
)

def likely_apartment(address):
    """
    >>> likely_apartment('apt 24 at 1 main st')
    True
    >>> likely_apartment('bsmt, 10 commercial st')
    True
    >>> likely_apartment('15 Park Ave')
    False
    """
    return bool(APARTMENT_TERM_CRX.search(address))


def find_similar(site, event):
    """
    Finds a single site similar to @site.

    Two sites are similar if at least one of:
    (i) The addresses imply an apartment and the addresses and names have
        matching metaphones.
    (ii) The addresses do not imply an apartment and the geocoded co-ords
         are within 4 metres of each other.
    (iii) Their name metaphone and normalised phone numbers match.
    """
    # split on probable apartment or not
    if not likely_apartment(site.address):
        # geospatial search ## NOTE: THIS DOES NOT WORK ON DEV_APPENGINE 
        # (as per https://code.google.com/p/googleappengine/issues/detail?id=7769 )
        r = search.Index('GEOSEARCH_INDEX').search(
            'distance(geopoint(%0.10f, %0.10f), loc) < 4' % (site.latitude, site.longitude)
        )
        if r.number_found > 0:
            for scored_doc in r.results:
                # check event matches
                possible_site_match = Site.get(scored_doc.doc_id)
                if possible_site_match and possible_site_match.event.key() == event.key():
                    return possible_site_match
    else:
        # is likely an apartment => compare metaphones
        if site.address_metaphone and site.name_metaphone:
            q = db.GqlQuery(
                "SELECT * FROM Site "
                "WHERE name_metaphone=:1 AND address_digits=:2 AND address_metaphone=:3",
                site.name_metaphone, site.address_digits, site.address_metaphone
            )
            if q.count() != 0:
                return q[0]

    # fallback to similar name and phone number
    if site.phone_normalised and site.name_metaphone:
        q = db.GqlQuery(
            "SELECT * FROM Site WHERE event=:1 "
            "AND name_metaphone=:2 and phone_normalised=:3",
            event.key(),
            site.name_metaphone,
            site.phone_normalised)
        if q.count() != 0:
            return q[0]
    
    # no similar match
    return None


def SiteToDict(site):

  site_dict = to_dict(site)
  site_dict["id"] = site.key().id()
  #claimed_by = None
  #try:
    #claimed_by = site.claimed_by
  #except db.ReferencePropertyResolveError:
    #pass
  #if claimed_by:
    #site_dict["claimed_by"] = {"name": claimed_by.name}
  #reported_by = None
  #try:
    #reported_by = site.reported_by
  #except db.ReferencePropertyResolveError:
    #pass
  #if reported_by:
    #site_dict["reported_by"] = {"name": reported_by.name}
  return site_dict

def SiteAndPhaseToDict(site, phase_name):
  site_dict = to_dict(site)
  site_dict["id"] = site.key().id()
  claimed_by = None
  raise Exception(site)
  try:
    claimed_by = site.claimed_by
  except db.ReferencePropertyResolveError:
    pass
  if claimed_by:
    site_dict["claimed_by"] = {"name": claimed_by.name}
  reported_by = None
  try:
    reported_by = site.reported_by
  except db.ReferencePropertyResolveError:
    pass
  if reported_by:
    site_dict["reported_by"] = {"name": reported_by.name}
  return site_dict


# We cache each site together with the AJAX necessary to
# serve it, since it is expensive to generate.
cache_prefix = Site.__name__ + "-d:"
cache_time = 3600
def GetCached(site_id):
  result = memcache.get(site_id, key_prefix = cache_prefix)
  if result:
    return result
  site = Site.get_by_id(site_id)
  cache_entry = (site, SiteToDict(site))
  memcache.set(cache_prefix + str(site_id), cache_entry,
               time = cache_time)
  return cache_entry

def PutAndCache(site):
  site.compute_similarity_matching_fields()
  site.put()

  # geospatial index ## NOTE: THIS DOES NOT WORK ON DEV_APPENGINE 
  # (as per https://code.google.com/p/googleappengine/issues/detail?id=7769 )
  search_doc = search.Document(
    doc_id=str(site.key()),
    fields=[
      search.GeoField(name='loc', value=search.GeoPoint(site.latitude, site.longitude))
  ])
  search.Index(name='GEOSEARCH_INDEX').put(search_doc)
  return memcache.set(cache_prefix + str(site.key().id()),
                      (site, SiteToDict(site)),
                      time = cache_time)

def GetAndCache(site_d):
  site = Site.get_by_id(site_d)
  if site:
    memcache.set(cache_prefix + str(site.key().id()),
                 (site, SiteToDict(site)),
                 time = cache_time)
  return site

def GetReference(obj, prop, values):
  try:
    key = prop.get_value_for_datastore(obj)
    if key:
      return values[key]
    return None
  except db.ReferencePropertyResolveError:
    return None

def GetSitesAndSetReferences(ids, events, organizations):
  sites = Site.get_by_id(ids)
  for site in sites:
    site.event = GetReference(site, Site.event, events)
    site.claimed_by = GetReference(site, Site.claimed_by, organizations)
    site.reported_by = GetReference(site, Site.reported_by, organizations)
  return sites

def GetAllCached(event, ids = None):
  if ids == None:
    q = Query(model_class = Site, keys_only = True)
    q.filter("event =", event)
    ids = [key.id() for key in q.run(batch_size = 2000)]
  lookup_ids = [str(id) for id in ids]
  cache_results = memcache.get_multi(lookup_ids, key_prefix = cache_prefix)
  not_found = [id for id in ids if not str(id) in cache_results.keys()]
  data_store_results = []
  orgs = dict([(o.key(), o) for o in organization.GetAllCached()])
  events = dict([(e.key(), e) for e in event_db.GetAllCached()])
  if len(not_found):
    data_store_results = [(site, SiteToDict(site)) for site in
                          GetSitesAndSetReferences(not_found, events, orgs)]
    memcache.set_multi(dict([(str(site[0].key().id()), site)
                             for site in data_store_results]),
                       key_prefix = cache_prefix,
                       time = cache_time)

  sites = cache_results.values() + data_store_results
  return sites

def _filter_non_digits(s):
    return ''.join(filter(lambda x: x.isdigit(), s))


class StandardSiteForm(model_form(Site)):
    pass


  
