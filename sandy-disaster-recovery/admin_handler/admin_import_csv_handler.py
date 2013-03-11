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
# System libraries.
from __future__ import with_statement
import cStringIO
import logging
import os
import pickle
from copy import copy

from google.appengine.ext import deferred
from google.appengine.ext import db, blobstore
from google.appengine.api import files
from google.appengine.runtime.apiproxy_errors import OverQuotaError

# Local libraries.
import base
import site_db
import event_db
import organization

from csv_utils import UnicodeReader, UnicodeWriter

# constants
GLOBAL_ADMIN_NAME = "Admin"

TRUE_VALUES = ['y', 'yes', 'true', '1']
FALSE_VALUES = ['n', 'no', 'false', '0', 'null']


#
# construct lookups
#

FIELD_NAMES_TO_EXCLUDE = {'case_number', 'event', 'latitude', 'longitude', 'blurred_latitude', 'blurred_longitude'}

FIELD_NAMES = [
    field_name for field_name in site_db.Site.CSV_FIELDS
    if field_name not in FIELD_NAMES_TO_EXCLUDE
]


FIELD_TYPES = {
    field_name: type(getattr(site_db.Site, field_name))
    for field_name in FIELD_NAMES
}

EXPLICITLY_REQUIRED_FIELDS = [
    'name', 'address', 'city', 'state', 'phone1', 'work_type',
]

EXAMPLE_DATA = {
    'name': 'Mr Example',
    'address': '!!REMOVE THIS EXAMPLE ROW!!',
    'city': 'New York City',
    'state': 'NY',
    'phone1': '555-555-5555',
    'work_type': 'ONE OF: %s' % ', '.join(site_db.Site.work_type.choices),
}

for field_name, field_type in FIELD_TYPES.items():
    example_value = {
        db.BooleanProperty: 'yes',
        db.IntegerProperty: '0',
        db.FloatProperty: '0.0',
        db.DateTimeProperty: '28/2/2013'
    }.get(field_type, None)
    if example_value:
        EXAMPLE_DATA[field_name] = example_value

#
# define CSV template rows
#

HEADINGS_ROW = FIELD_NAMES
EXAMPLES_ROW = [EXAMPLE_DATA.get(name, '') for name in FIELD_NAMES]


#
# models
# 

class CSVFile(db.Model):
    filename = db.StringProperty(required=True)
    creation_timestamp = db.DateTimeProperty(auto_now_add=True, required=True)
    event = db.ReferenceProperty(event_db.Event, required=True)
    blob = blobstore.BlobReferenceProperty(required=True)
    total_row_count = db.IntegerProperty(required=True)
    analysed_row_count = db.IntegerProperty(default=0, required=True)
    valid_row_count = db.IntegerProperty(default=0, required=True)
    invalid_row_count = db.IntegerProperty(default=0, required=True)
    saved_count = db.IntegerProperty(default=0, required=True)
    header_present = db.BooleanProperty(default=True, required=True)
    analysis_started = db.BooleanProperty(default=False, required=True)
    analysis_complete = db.BooleanProperty(default=False, required=True)
    analysis_failed = db.BooleanProperty(default=False, required=True)
    saving = db.BooleanProperty(default=False, required=True)
    deleting = db.BooleanProperty(default=False, required=True)

class CSVRow(db.Model):
    csv_file = db.ReferenceProperty(CSVFile, required=True)
    num = db.IntegerProperty(required=True)
    saved = db.BooleanProperty(default=False, required=True)
    row = db.ListProperty(unicode, required=True)
    row_dict = db.BlobProperty()
    validation = db.BlobProperty()
    geocoded_address = db.BlobProperty()


#
# functions
#

def write_csv_template(fd):
    writer = UnicodeWriter(fd)
    writer.writerow(HEADINGS_ROW)
    writer.writerow(EXAMPLES_ROW)



from dateutil.parser import parse as parse_date

def parse_field(field_name, field_type, field_value):
    """
    >>> parse_field(None, StringProperty, 'text')
    'text'
    >>> parse_field(None, StringProperty, '') # returns None
    >>> parse_field(None, IntegerProperty, u'1')
    1
    >>> parse_field(None, FloatProperty, u'1')
    1.0
    >>> parse_field(None, BooleanProperty, 'YES')
    True
    >>> parse_field(None, BooleanProperty, 'no')
    False
    >>> parse_field(None, BooleanProperty, 'other')
    'other'
    >>> parse_field(None, DateTimeProperty, '2/17/2013')
    datetime.datetime(2013, 2, 17, 0, 0)
    """
    if field_value == '':
        return None
    elif field_type == db.IntegerProperty:
        return int(field_value)
    elif field_type == db.FloatProperty:
        return float(field_value)
    elif field_type == db.BooleanProperty:
        if field_value.lower() in TRUE_VALUES:
            return True
        elif field_value.lower() in FALSE_VALUES:
            return False
        else:
            return field_value # handle error later
    elif field_type == db.DateTimeProperty:
        try:
            return parse_date(field_value, dayfirst=False) # assume American format
        except ValueError:
            return field_value # handle error later
    elif field_type == db.ReferenceProperty:
        # handle outside
        return field_value
    else:
        return field_value

def row_to_dict(event, field_names, row):
    d = {}
    for field_name, field_value in zip(field_names, row):
        field_type = FIELD_TYPES[field_name]

        # parse
        parsed_value = parse_field(field_name, field_type, field_value)

        # handle org references
        if field_name in ('reported_by', 'claimed_by'):
            results = db.GqlQuery(
                "SELECT * FROM Organization WHERE name=:1 AND incident=:2", field_value, event.key()
            )
            if results and results.count() == 1:
                d[field_name] = results[0].key().id()
            else:
                d[field_name] = parsed_value
        elif parsed_value != None:
            d[field_name] = parsed_value
    return d

import google_maps_utils


class ImportException(Exception): pass

class RowLengthException(ImportException):
    def __init__(self, expected, got):
        self.expected
        self.got

class FieldMissingException(ImportException):
    def __init__(self, field_name):
        self.field_name = field_name

class AddressUnknownException(ImportException):
    def __init__(self, address):
        self.address = address

from google.appengine.api.datastore_errors import BadValueError

def validate_row(event, row):
    """
    Validates @row for @event and returns (descriptive dict, geocoding) pair.
    """
    validation = {
        'row_length_ok': None,
        'contains_example_data': None,
        'missing_fields': [],
        'invalid_fields': {}, # {field_name: error_msg}
        'address_geocodes_ok': None,
        'validates': False, # assume false
    }

    # validate row length
    if not len(row) == len(FIELD_NAMES):
        validation['row_length_ok'] = False
        return validation, None
    else:
        validation['row_length_ok'] = True

    # validate does not contain example data
    row_d = row_to_dict(event, FIELD_NAMES, row)
    validation['contains_example_data'] = any(
        map(lambda s: 'example' in s or 'warning' in s,
            [val.lower() for val in row_d.values() if isinstance(val, basestring)])
    )
    if validation['contains_example_data']:
        return validation, None

    # validate explicitly required fields (as form_handler does)
    for field_name in EXPLICITLY_REQUIRED_FIELDS:
        if field_name not in row_d:
            validation['missing_fields'].append(field_name)
    if validation['missing_fields']:
        return validation, None

    # validate org ref fields are not strings
    validation_row_copy = copy(row_d)
    for field_name in ('reported_by', 'claimed_by'):
        if isinstance(row_d[field_name], basestring):
            validation['invalid_fields'][field_name] = 'Unknown organisation for this event'
        if field_name in validation_row_copy:
            del(validation_row_copy[field_name])

    # validate required fields and types
    # by attempting to construct Site multiple times
    error_encountered = False
    while True:
        try:
            site_db.Site(**validation_row_copy)
            if error_encountered:
                return validation, None
            else:
                break
        except BadValueError, e:
            field_name = e.message.split(' ')[1]
            if field_name in validation:
                return validation, None
            validation['invalid_fields'][field_name] = e.message
            del(validation_row_copy[field_name])
            error_encountered = True

    # bail out if any errors so far
    v = validation
    if any((not v['row_length_ok'], v['invalid_fields'], v['missing_fields'])):
        return validation, None

    # validate full address by geocoding
    full_address = ', '.join(
        filter(None, [
            row_d.get(name, None) for name in ['address', 'city', 'state']
        ])
    )
    try:
        geocode_result = google_maps_utils.geocode(full_address)
        validation['address_geocodes_ok'] = bool(geocode_result)
    except OverQuotaError:
        validation['address_geocodes_ok'] = False
    if not validation['address_geocodes_ok']:
        return validation, None

    # fully validated
    validation['validates'] = True
    return validation, geocode_result

def validation_to_text(validation):
    """
    Return readable description of @validation.
    """
    s = ""
    if not validation['row_length_ok']:
        s += "Row is incorrect length; "
    if validation['contains_example_data']:
        s += "Row contains example or warning text; "
    if validation['missing_fields']:
        s += "Missing fields: %s; " % ', '.join(validation['missing_fields'])
    if validation['invalid_fields']:
        s += "Invalid fields: %s; " % ', '.join(validation['invalid_fields'])
    if not s and not validation['address_geocodes_ok']:
        s += "Could not find address; "
    return "ERRORS: %s" % s

class HeaderException(Exception): pass

from google_maps_utils import geocoding_to_address_dict

def read_csv(event, fd):
    """
    Read CSV @fd to generate (row_num, row), checking for heading row first.
    """
    reader = UnicodeReader(fd)
    for row_num, row in enumerate(reader):
        if row_num == 0:
            # validate heading present
            if row_num == 0:
                # check heading row present then skip
                if row != HEADINGS_ROW:
                    missing = set(HEADINGS_ROW) - set(row)
                    unexpected = set(row) - set(HEADINGS_ROW)
                    raise HeaderException(
                        "Invalid header row detected: " +
                        "missing %s; unexpected %s" % (list(missing), list(unexpected))
                    )
                else:
                    continue
        else:
            yield row_num, row

def write_csv(fd, rows):
    writer = UnicodeWriter(fd)
    writer.writerow(HEADINGS_ROW)
    for row in rows:
        writer.writerow(row)

@db.transactional(retries=100)
def increment_counter(obj_key, counter_field_name, amount):
    obj = db.get(obj_key)
    setattr(obj, counter_field_name, getattr(obj, counter_field_name) + amount)
    obj.put()

@db.transactional(retries=100)
def inc_counter_and_check(obj_key, counter_field, comparison_field, flag_field, flag_value=True, amount=1):
    """
    Increment @counter_field of obj with @obj_key by @amount.

    If @counter_field value matches value of @comparison_field,
    set @flag_field to @flag_value.
    """
    obj = db.get(obj_key)
    new_counter_val = getattr(obj, counter_field) + amount
    setattr(obj, counter_field, new_counter_val)
    if new_counter_val == getattr(obj, comparison_field):
        setattr(obj, flag_field, flag_value)
    obj.put()

def analyse_row(csv_file_obj_key, csv_row_obj_key):
    csv_file_obj = CSVFile.get(csv_file_obj_key)
    csv_row_obj = CSVRow.get(csv_row_obj_key)
    event = csv_file_obj.event
    row = csv_row_obj.row
    validation, geocoding = validate_row(event, row)
    geocoded_address = geocoding_to_address_dict(geocoding) if geocoding else None
    row_dict = row_to_dict(event, FIELD_NAMES, row)
    csv_row_obj.row_dict = pickle.dumps(row_dict)
    csv_row_obj.validation = pickle.dumps(validation)
    csv_row_obj.geocoded_address = pickle.dumps(geocoded_address)
    csv_row_obj.save()

    # increment counters
    inc_counter_and_check(
        csv_file_obj.key(), 'analysed_row_count', 'total_row_count', 'analysis_complete'
    )
    if validation['validates']:
        increment_counter(csv_file_obj.key(), 'valid_row_count', 1)
    else:
        increment_counter(csv_file_obj.key(), 'invalid_row_count', 1)


def write_valid_from_csv(csv_id):
    """
    Save valid rows for CSV file with @csv_id to the database.
    """
    csv_file_obj = CSVFile.get_by_id(int(csv_id))
    csv_file_obj.saving = True
    csv_file_obj.save()
    csv_rows = db.GqlQuery(
        "SELECT * from CSVRow WHERE csv_file=:1 and saved=False", csv_file_obj.key()
    )
    for i, csv_row_obj in enumerate(csv_rows):
        deferred.defer(
            write_valid_row,
            csv_file_obj.key(),
            csv_row_obj.key(),
            _countdown=i
        )

def write_valid_row(csv_file_obj_key, csv_row_obj_key):
    csv_file_obj = CSVFile.get(csv_file_obj_key)
    csv_row_obj = CSVRow.get(csv_row_obj_key)
    row_dict = pickle.loads(csv_row_obj.row_dict)
    validation = pickle.loads(csv_row_obj.validation)
    geocoded_address = pickle.loads(csv_row_obj.geocoded_address)
    if validation['validates']: 
        for gc_field_name, gc_field_value in geocoded_address.items():
            if not row_dict.get(gc_field_name, None):
                row_dict[gc_field_name] = gc_field_value
        for org_field_name in ['reported_by', 'claimed_by']:
            if row_dict.get(org_field_name, None):
                row_dict[org_field_name] = (
                    organization.Organization.get_by_id(row_dict[org_field_name])
                )
        new_site = site_db.Site(**row_dict)
        new_site.save()
        event_db.AddSiteToEvent(new_site, csv_file_obj.event.key().id())

        # update counters
        csv_row_obj.saved = True
        csv_row_obj.save()
        inc_counter_and_check(
            csv_file_obj.key(), 'saved_count', 'valid_row_count', 'saving', flag_value=False
        )


def delete_csv(csv_id):
    csv_file_obj = CSVFile.get_by_id(int(csv_id))
    csv_file_obj.deleting = True
    csv_file_obj.save()
    csv_rows = db.GqlQuery("SELECT * from CSVRow WHERE csv_file=:1", csv_file_obj.key())
    for csv_row in csv_rows:
        csv_row.delete()
    blobstore.BlobInfo.get(csv_file_obj.blob.key()).delete() 
    csv_file_obj.delete()


def invalid_rows_to_csv(csv_file_obj):
    csv_rows = db.GqlQuery(
        "SELECT * from CSVRow WHERE csv_file=:1 and saved=False", csv_file_obj.key()
    )
    output_rows = []
    for csv_row_obj in csv_rows:
        validation = pickle.loads(csv_row_obj.validation)
        if validation['validates'] == False:
            output_rows.append(
                csv_row_obj.row + [validation_to_text(validation)]
            )
    return output_rows



#
# templates
#

import jinja2
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals.update(zip=zip)
import_template = jinja_environment.get_template('admin_import_csv.html')
check_template = jinja_environment.get_template('admin_import_csv_check.html')


#
# webapp handlers
#

class ImportCSVHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    # check auth
    global_admin = False
    local_admin = False
    
    if org.name == GLOBAL_ADMIN_NAME:
            global_admin = True
    if org.is_admin == True and global_admin == False:
            local_admin = True
            
    if global_admin == False and local_admin == False:
            self.redirect("/")
            return

    # return form
    active_csvs = db.GqlQuery("SELECT * FROM CSVFile")
    events_list = db.GqlQuery("SELECT * FROM Event ORDER BY created_date DESC")
    self.response.out.write(import_template.render({
        'global_admin': global_admin,
        'active_csvs': active_csvs,
        'events_list': events_list,
        'valid_work_types': str(site_db.Site.work_type.choices)[1:-1],
    }))

  def AuthenticatedPost(self, org, event):
    # check auth
    global_admin = False
    local_admin = False
    
    if org.name == GLOBAL_ADMIN_NAME:
        global_admin = True
    if org.is_admin == True and global_admin == False:
        local_admin = True    
    if global_admin == False and local_admin == False:
        self.redirect("/")
        return

    # get action param
    action = self.request.get('action')

    # no action => upload & analyse CSV
    if not action:
      # get params
      event_id = self.request.get('choose_event')
      if not event_id:
        self.response.out.write('No event selected.')
        return
      event = event_db.GetEventFromParam(event_id)
      try:
        csv_file = self.request.params['csv_file'].file
        csv_filename = self.request.params['csv_file'].filename
      except AttributeError:
        self.response.out.write('No file supplied.')
        return
    
      # store csv file to blobstore
      blob_filename = files.blobstore.create(
        mime_type='application/octet-stream',
        _blobinfo_uploaded_filename=csv_filename
      )
      with files.open(blob_filename, 'a') as f:
        f.write(csv_file.read())
      files.finalize(blob_filename)
      blob_key = files.blobstore.get_blob_key(blob_filename)

      # create csv file object
      blob_fd = blobstore.BlobReader(blob_key)
      blob_fd.seek(0)
      total_row_count = len(blob_fd.readlines()) - 1
      csv_file_obj = CSVFile(
        filename=csv_filename,
        event=event.key(),
        blob=blob_key,
        total_row_count=total_row_count,
        analysis_started=True
      )
      csv_file_obj.save()

      # create csv row objects
      blob_fd.seek(0)
      try:
          for row_num, row in read_csv(event, blob_fd):
            csv_row_obj = CSVRow(
                parent=csv_file_obj.key(),
                csv_file=csv_file_obj.key(),
                num=row_num,
                row=row
            )
            csv_row_obj.save()

            # analyse row in background
            deferred.defer(analyse_row, csv_file_obj.key(), csv_row_obj.key())
      except HeaderException:
          csv_file_obj.header_present = False
          csv_file_obj.save()
          self.redirect('/admin-import-csv')
          return

      self.redirect('/admin-import-csv')
      return

    # delete csv file action
    if action == "delete":
        csv_id = self.request.get('csv_id')
        deferred.defer(delete_csv, csv_id)
        self.redirect('/admin-import-csv')
        return


class ActiveCSVImportHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        csv_id = self.request.get('id', None)

        # get csv rows & unpickle fields
        csv_file_obj = CSVFile.get_by_id(int(csv_id))
        csv_rows = db.GqlQuery(
            "SELECT * from CSVRow WHERE csv_file=:1 ORDER BY num ASC", csv_file_obj.key()
        )
        annotated_rows = [{
            'num': cro.num,
            'row': cro.row,
            'row_dict': pickle.loads(cro.row_dict),
            'validation': pickle.loads(cro.validation),
            'geocoded_address': pickle.loads(cro.geocoded_address),
        } for cro in csv_rows]

        # write out page
        self.response.out.write(check_template.render({
            ##'global_admin': global_admin,
            'event': event,
            'form': site_db.SiteForm(),
            'csv_file_obj': csv_file_obj,
            'csv_id': csv_id, 
            'field_names': FIELD_NAMES,
            'annotated_rows': annotated_rows,
            'valid_row_count': csv_file_obj.valid_row_count,
            'invalid_row_count': csv_file_obj.invalid_row_count,
        }))

    def AuthenticatedPost(self, org, event):
        action = self.request.get('action', None)
        # action write valid rows
        if action == 'write':
            csv_id = int(self.request.get('csv_id'))
            deferred.defer(write_valid_from_csv, csv_id)
            self.redirect('/admin-import-csv')
            return

        # action download invalid CSV
        if action == 'download_invalid_csv':
            csv_id = int(self.request.get('csv_id'))
            csv_file_obj = CSVFile.get_by_id(int(csv_id))
            warning_row = [
              'WARNING: error messages', 'have been added',
              'at the far right', 'of each row. ',
              'Remove them', 'and this row', 'before resubmitting.'
            ]
            rows_for_csv = [warning_row] + invalid_rows_to_csv(csv_file_obj)
            s = cStringIO.StringIO()
            write_csv(s, rows_for_csv)
            s.seek(0)
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.out.write(s.read())
            return



class GetCSVTemplateHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        self.response.headers['Content-Type'] = 'text/csv'
        write_csv_template(self.response.out)
