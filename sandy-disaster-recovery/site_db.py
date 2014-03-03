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
from google.appengine.api import search
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField

# Local libraries.
from indexed import SearchIndexedExpandoModel
from memcache_utils import memcached
from appengine_utils import deserialize_entity, generate_from_search, search_doc_to_dict
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

SHORT_STATUS_OPEN = u'Open'
SHORT_STATUS_CLOSED = u'Closed'

STATUSES_UNICODE = map(unicode, STATUSES)


class Site(SearchIndexedExpandoModel):

  CACHE_TAGS = {'SiteCaches'}

  # The list of fields that will be included in the CSV output.
  CSV_FIELDS = []

  # Data about the site itself.
  name = db.StringProperty(required = True)
  case_number = db.StringProperty()
  event = db.ReferenceProperty(event_db.Event)
  reported_by = db.ReferenceProperty(organization.Organization,
                                     collection_name="reported_site_set")
  reported_by_name = db.StringProperty()  # (denorm)
  claimed_by = db.ReferenceProperty(organization.Organization,
                                    collection_name="claimed_site_set")
  claimed_by_name = db.StringProperty()  # (denorm)
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

  ## Priority assigned by organization (1 is highest).
  priority = db.IntegerProperty(choices=[1, 2, 3, 4, 5], default = 3)
  
  #priority = db.StringProperty()
  ## Name of org. rep (e.g. "Jill Smith")
  #inspected_by = db.StringProperty()
  ## Name of org. rep (e.g. "Jill Smith")
  #prepared_by = db.StringProperty()
  ## Do not work before
  #do_not_work_before = db.StringProperty()

  status = db.StringProperty(
    choices=STATUSES,
    default="Open, unassigned"
  )
  short_status = db.StringProperty()
  
  open_phases_list = db.StringListProperty()

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

  @property
  def county_and_state(self):
      return (
          (self.county if self.county else u'[Unknown]') +
          ((u', %s' % self.state) if self.state else u'')
      )

  def to_dict(self):
      " No datastore lookups allowed here - slows bulk lookups. "
      return dict(
          to_dict(self),
          id=self.key().id(),
          claimed_by={
              "name": self.claimed_by_name
          } if self.claimed_by_name else None,
          reported_by={
              "name": self.reported_by_name
          } if self.reported_by_name else None,
      )

  @property
  def as_dict(self):
      " Property synonym "
      return self.to_dict()

  def before_put(self):
      super(Site, self).before_put()
      self.compute_similarity_matching_fields()

      # set short status
      self.short_status = (
          SHORT_STATUS_OPEN
          if self.status.startswith('Open')
          else SHORT_STATUS_CLOSED
      )

      # denorm name fields from referenced orgs
      if self.reported_by:
          self.reported_by_name = self.reported_by.name
      if self.claimed_by:
          self.claimed_by_name = self.claimed_by.name

      # set blurred co-ordinates
      self.blurred_latitude = self.latitude + random.uniform(-0.001798, 0.001798)
      self.blurred_longitude = self.longitude + random.uniform(-0.001798, 0.001798)

  def after_put(self):
      super(Site, self).after_put()
      # geospatial index ## NOTE: THIS DOES NOT WORK ON DEV_APPENGINE 
      # (as per https://code.google.com/p/googleappengine/issues/detail?id=7769 )
      search_doc = search.Document(
        doc_id=str(self.key()),
        fields=[
          search.GeoField(name='loc', value=search.GeoPoint(self.latitude, self.longitude))
      ])
      search.Index(name='GEOSEARCH_INDEX').put(search_doc)


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

  def indexes_and_fields(self):
      return [
          (search.Index('SiteCompleteIndex'), [
              search.TextField('s', self.serialized),
              search.AtomField('id', unicode(self.key().id())),
              search.AtomField('event_key', unicode(self.event.key())),
              search.AtomField('case_number', self.case_number),
              search.AtomField('short_status', self.short_status),
          ]),
          (search.Index('SitePinIndex'), [
              search.AtomField('id', unicode(self.key().id())),
              search.AtomField('event_key', unicode(self.event.key())),
              search.AtomField('case_number', self.case_number),
              search.AtomField('status', self.status),
              search.AtomField('short_status', self.short_status),
              search.AtomField('work_type', self.work_type),
              search.NumberField('latitude', self.latitude),
              search.NumberField('longitude', self.longitude),
              search.TextField('name', self.name),
              search.TextField('address', self.address),
              search.TextField('city', self.city),
              search.TextField('county', self.county),
              search.TextField('state', self.state),
              search.TextField('zip_code', self.zip_code),
              search.TextField('reported_by_name', self.reported_by_name),
              search.TextField('claimed_by_name', self.claimed_by_name),
          ]),
          (search.Index('SitePublicPinIndex'), [
              search.AtomField('event_key', unicode(self.event.key())),
              search.AtomField('case_number', self.case_number),
              search.AtomField('status', self.status),
              search.AtomField('short_status', self.short_status),
              search.AtomField('work_type', self.work_type),
              search.NumberField('blurred_latitude', self.blurred_latitude),
              search.NumberField('blurred_longitude', self.blurred_longitude),
          ]),
      ]

  @classmethod
  @memcached(cache_tag='SiteCaches')
  def in_event(cls, event_key, n, page, short_status=None):
      search_index = search.Index('SiteCompleteIndex')
      query_str = (
          u'event_key:%s' % unicode(event_key) +
          (u' short_status:%s' % short_status) if short_status else u''
      )
      results = generate_from_search(search_index, query_str, n, n*page)
      return [deserialize_entity(hit['s'][0].value) for hit in results]

  @classmethod
  @memcached(cache_tag='SiteCaches')
  def pins_in_event(cls, event_key, n, page, short_status=None):
      search_index = search.Index('SitePinIndex')
      query_str = (
          u'event_key:%s' % unicode(event_key) +
          (u' short_status:%s' % short_status) if short_status else u''
      )
      results = generate_from_search(search_index, query_str, n, n*page)

      def augment_connected_orgs(d):
          " Meets expectation of existing interface. "
          del(d['event_key'])
          d['reported_by'] = (
              {'name': d['reported_by_name']}
              if d['reported_by_name'] else None
          )
          d['claimed_by'] = (
              {'name': d['claimed_by_name']}
              if d['claimed_by_name'] else None
          )
          return d

      return map(augment_connected_orgs, map(search_doc_to_dict, results))

  @classmethod
  @memcached(cache_tag='SiteCaches')
  def public_pins_in_event(cls, event_key, n, page, short_status=None):
      search_index = search.Index('SitePublicPinIndex')
      query_str = (
          u'event_key:%s' % unicode(event_key) +
          (u' short_status:%s' % short_status) if short_status else u''
      )
      results = generate_from_search(search_index, query_str, n, n*page)

      def filter_fields(d):
          del(d['event_key'])
          del(d['short_status'])
          return d

      return map(filter_fields, map(search_doc_to_dict, results))

  @classmethod
  def by_ids(cls, event, ids):
      ids = set(ids)
      for site in cls.all_in_event(event.key()):
          if site.key().id() in ids:
              yield site


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
  claimed_by = None
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


def PutAndCache(site):
  # legacy interface
  site.put()


def GetAndCache(site_d):
  # legacy interface
  site = Site.get_by_id(site_d)
  return site


def _filter_non_digits(s):
    return ''.join(filter(lambda x: x.isdigit(), s))


class StandardSiteForm(model_form(Site)):
    pass


  
