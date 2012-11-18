# System libraries.
import datetime
import logging
import wtforms.ext.dateutil.fields
import wtforms.fields
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
from google.appengine.api import memcache
import json
from google.appengine.ext.db import Query

# Local libraries.
import cache
import event_db
import organization

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
    logging.warn('site %s is missing attribute' % (site.key().id(), field))
    return None

class Site(db.Model):
  # The list of fields that will be included in the CSV output.
  CSV_FIELDS = []

  # Data about the site itself.
  name = db.StringProperty(required = True)
  case_number = db.StringProperty()
  event = db.ReferenceProperty(event_db.Event)
  reported_by = db.ReferenceProperty(organization.Organization,
                                     collection_name="reported_site_set")
  claimed_by = db.ReferenceProperty(organization.Organization,
                                    collection_name="claimed_site_set")
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
  time_to_call = db.StringProperty()
  rent_or_own = db.StringProperty(choices=["Rent", "Own"])
  work_without_resident = db.BooleanProperty()
  member_of_assessing_organization = db.BooleanProperty()
  first_responder = db.BooleanProperty()
  older_than_60 = db.BooleanProperty()
  disabled = db.BooleanProperty()
  special_needs = db.StringProperty(multiline=True)
  electricity = db.BooleanProperty()
  standing_water = db.BooleanProperty()
  tree_damage = db.BooleanProperty()
  tree_damage_details = db.StringProperty(multiline=True)
  habitable = db.BooleanProperty(default = True)
  work_requested = db.StringProperty(multiline=True)
  others_help = db.StringProperty(multiline=True)
  debris_removal_only = db.BooleanProperty()
  work_type = db.StringProperty(choices=["Flood", "Trees", "Other",
                                         "Unknown", "Goods or Services"])
  flood_height = db.StringProperty()
  floors_affected = db.StringProperty(choices=[
      "Basement Only",
      "Basement and Ground Floor",
      "Ground Floor Only"])
  carpet_removal = db.BooleanProperty()
  hardwood_floor_removal = db.BooleanProperty()
  drywall_removal = db.BooleanProperty()
  heavy_item_removal = db.BooleanProperty()
  appliance_removal = db.BooleanProperty()
  standing_water = db.BooleanProperty()
  mold_remediation = db.BooleanProperty()
  pump_needed = db.BooleanProperty()
  num_trees_down = db.IntegerProperty(
      choices = [0, 1, 2, 3, 4, 5], default = 0)
  num_wide_trees = db.IntegerProperty(
      choices = [0, 1, 2, 3, 4, 5], default = 0)
  roof_damage = db.BooleanProperty()
  tarps_needed = db.IntegerProperty(default = 0)

  goods_and_services = db.StringProperty(multiline = True)
  tree_diameter = db.StringProperty()
  electrical_lines = db.BooleanProperty()
  cable_lines = db.BooleanProperty()
  cutting_cause_harm = db.BooleanProperty()
  other_hazards = db.StringProperty(multiline = True)
  insurance = db.StringProperty(multiline = True)
  notes = db.TextProperty()
  latitude = db.FloatProperty(default = 0.0)
  longitude = db.FloatProperty(default = 0.0)
  # Priority assigned by organization (1 is highest).
  priority = db.IntegerProperty(choices=[1, 2, 3, 4, 5], default = 3)
  # Name of org. rep (e.g. "Jill Smith")
  inspected_by = db.StringProperty()
  # Name of org. rep (e.g. "Jill Smith")
  prepared_by = db.StringProperty()
  # Do not work before
  do_not_work_before = db.StringProperty()

  # Metadata
  status = db.StringProperty(choices=[
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
      ],
      default="Open, unassigned")

  date_closed = db.DateTimeProperty()
  # Number of volunteers who helped.
  total_volunteers = db.FloatProperty(default = 0.0)
  # Number of hours that each volunteer worked.
  # There's apparently an assumption that all volunteers worked the same amount
  # of time, since total time for the project is calculated as
  # total_volunteers * hours_worked_per_volunteer.
  hours_worked_per_volunteer = db.FloatProperty(default = 0.0)
  # The initials of the resident who was present for the work.
  initials_of_resident_present = db.StringProperty()

  # Defines the order of fields for CSV output.
  CSV_FIELDS = [
      'case_number',
      'name',
      'reported_by',
      'claimed_by',
      'request_date',
      'address',
      'city',
      'county',
      'state',
      'zip_code',
      'cross_street',
      'landmark',
      'phone1',
      'phone2',
      'time_to_call',
      'rent_or_own',
      'work_without_resident',
      'older_than_60',
      'disabled',
      'special_needs',
      'electricity',
      'standing_water',
      'tree_damage',
      'tree_damage_details',
      'habitable',
      'work_requested',
      'others_help',
      'debris_removal_only',
      'work_type',
      'flood_height',
      'floors_affected',
      'carpet_removal',
      'drywall_removal',
      'heavy_item_removal',
      'standing_water',
      'pump_needed',
      'num_trees_down',
      'num_wide_trees',
      'roof_damage',
      'tarps_needed',
      'goods_and_services',
      'tree_diameter',
      'electrical_lines',
      'cable_lines',
      'cutting_cause_harm',
      'other_hazards',
      'insurance',
      'notes',
      'latitude',
      'longitude',
      'priority',
      'inspected_by',
      'status',
      'date_closed',
      'total_volunteers',
      'hours_worked_per_volunteer',
      'event',
      'initials_of_resident_present',
      'member_of_assessing_organization',
      'first_responder',
      'hardwood_floor_removal',
      'mold_remediation',
      'appliance_removal',
      'do_not_work_before',
      'prepared_by',
      ]

  _CSV_ACCESSORS = {
    'reported_by': _GetOrganizationName,
    'claimed_by': _GetOrganizationName,
    }

  def ToCsvLine(self):
    """Returns the site as a list of string values, one per field in
    CSV_FIELDS."""
    csv_row = []
    for field in self.CSV_FIELDS:
      accessor = self._CSV_ACCESSORS.get(field, _GetField)
      value = accessor(self, field)
      if value is None:
        csv_row.append('')
      else:
        try:
          csv_row.append(unicode(value).encode("utf-8"))
        except:
          logging.critical("Failed to parse: " + value + " " + str(self.key().id()))
    return csv_row

def _ValidateCsvFields():
  """Ensures that there is an entry in Sites.CSV_FIELDS for every db
  property."""
  # NOTE(Bruce): If there's ever a field that we don't want to include in CSV
  # output, we can add an exclusion list, and ensure that CSV_FIELDS + the
  # exclusion list covers all properties.
  missing = set(Site.fields()) - set(Site.CSV_FIELDS)
  if missing:
    raise ValueError('CSV_FIELDS is missing entries for these properties: %s' %
                     ', '.join(missing))
_ValidateCsvFields()
del _ValidateCsvFields

SiteForm2 = model_form(Site)

def _ChoicesWithBlank(choices):
  """Converts a list items into choices suitable for a wtforms choices list.
  Prepends a blank value to the list to ensure that a user has to purposefully
  choose all values.
  """
  return [('', '--Choose One--')] + [(choice, choice) for choice in choices]

class SiteForm(SiteForm2):
  priority = wtforms.fields.RadioField(
      choices = [(5, ""), (4, ""), (3, ""), (2, ""), (1, "")],
      coerce = int,
      default = 3)
  num_trees_down = wtforms.fields.SelectField(
      choices = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, "5+")],
      coerce = int,
      default = 0)
  num_wide_trees = wtforms.fields.SelectField(
      choices = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, "5+")],
      coerce = int,
      default = 0)
  request_date = wtforms.ext.dateutil.fields.DateTimeField(
      default = datetime.datetime.now())

  floors_affected = wtforms.fields.SelectField(
      choices=_ChoicesWithBlank(Site.floors_affected.choices))
  rent_or_own = wtforms.fields.SelectField(
      choices=_ChoicesWithBlank(Site.rent_or_own.choices))
  work_type_choices = _ChoicesWithBlank(Site.work_type.choices)
  for i in range(len(work_type_choices)):
    if work_type_choices[i][0] == "Trees":
      work_type_choices[i] = ("Trees", "Trees or Wind")
  work_type = wtforms.fields.SelectField(choices=work_type_choices)

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

# We cache each site together with the AJAX necessary to
# serve it, since it is expensive to generate.
cache_prefix = Site.__name__ + "-d:"
cache_time = 3600
def GetCached(site_id):
  result = cache.GetLocal(cache_prefix + site_id)
  if not result:
    result = memcache.get(site_id, key_prefix = cache_prefix)
    if not result:
      site = Site.get_by_id(site_id)
      result = (site, SiteToDict(site))
      memcache.set(cache_prefix + str(site_id), result,
                   time = cache_time)
    SetLocal(cache_prefix + site_id, result, cache_time)
  return result

def PutAndCache(site):
  site.put()
  cache_key = cache_prefix + str(site.key().id())
  cache_entry = (site, SiteToDict(site))
  cache.SetLocal(cache_key, cache_entry, cache_time)
  return memcache.set(cache_key, cache_entry,
                      time = cache_time)

def GetAndCache(site_d):
  site = Site.get_by_id(site_d)
  if site:
    cache_key = cache_prefix + str(site.key().id())
    cache_entry = (site, SiteToDict(site))
    cache.SetLocal(cache_key, cache_entry, cache_time)
    memcache.set(cache_key,
                 cache_entry,
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

cache_ids = False
def GetSitesAndSetReferences(ids, events, organizations):
  sites = Site.get_by_id(ids)
  for site in sites:
    site.event = GetReference(site, Site.event, events)
    site.claimed_by = GetReference(site, Site.claimed_by, organizations)
    site.reported_by = GetReference(site, Site.reported_by, organizations)
  return sites

def GetAllCached(event, county = "all", ids = None):
  refresh_counties = (county == "all" and ids == None)
  if not ids:
    if cache_ids:
      cache_key_for_ids = "SiteDictIds:" + event.key().id() + ":" + county 
      ids = memcache.get(cache_key_for_ids)
      if not ids:
        # Retrieve all matching keys. As a keys_only scan,
        # This should be more efficient than a full data scan.
        q = Query(model_class = Site, keys_only = True)
        q.filter("event =", event)
        if county != all:
          q.filter("county =", county)
        ids = [key.id() for key in q]
        # Cache these for up to six minutes.
        # TODO(Jeremy): This may do more harm than
        # good, depending on how often
        # people reload the map.
        memcache.set(cache_key_for_ids, ids,
                     time = 360)
    else:
      q = Query(model_class = Site, keys_only = True)
      q.filter("event =", event)
      if county != "all":
        q.filter("county =", county)
    
      ids = [key.id() for key in q.run(batch_size = 2000)]
  lookup_ids = [str(id) for id in ids]
  cache_results = cache.GetMulti(lookup_ids, key_prefix = cache_prefix, time_sec = cache_time)
  not_found = [id for id in ids if not str(id) in cache_results.keys()]
  data_store_results = []
  orgs = dict([(o.key(), o) for o in organization.GetAllCached()])
  events = dict([(e.key(), e) for e in event_db.GetAllCached()])
  if len(not_found):
    data_store_results = [(site, SiteToDict(site)) for site in
                          GetSitesAndSetReferences(not_found, events, orgs)]
    cache.SetMulti(dict([(str(site[0].key().id()), site)
                         for site in data_store_results]),
                   cache_prefix,
                   cache_time)

  sites = cache_results.values() + data_store_results
  
  if refresh_counties:
    counties = {}
    for s in sites:
      current_county = s[0].county
      if not current_county in counties:
        counties[current_county] = (1, s[0].latitude, s[0].longitude)
      else:
        counties[current_county] = (counties[current_county][0] + 1,
                                    counties[current_county][1] + s[0].latitude,
                                    counties[current_county][2] + s[0].longitude)
    county_positions = {}
    for current_county in counties.keys():
      county_positions[current_county] = (counties[current_county][1] / counties[current_county][0],
                                          counties[current_county][2] / counties[current_county][0])
    if len(county_positions) < 20:
      for i in range(len(event.counties)):
        if not event.counties[i] in county_positions.keys():
          county_positions[event.counties[i]] = (event.latitudes[i], event.longitudes[i])
    event_db.SetCountiesForEvent(event.key().id(), county_positions)

  return sites
