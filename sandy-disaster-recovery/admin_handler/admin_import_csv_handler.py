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
import datetime
import jinja2
import logging
import math
import os
import csv
from copy import copy

from google.appengine.ext import db, blobstore
from google.appengine.api import files
from google.appengine.ext.db import (
    BooleanProperty, StringProperty, IntegerProperty, FloatProperty, DateTimeProperty,
    ReferenceProperty
)

# Local libraries.
import base
import site_util
import site_db
import event_db

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

ADDITIONALLY_REQUIRED_FIELDS = [
    'name', 'phone1', 'city', 'state', 'work_type',
]

EXAMPLE_DATA = {
    'name': 'Mr Example',
    'address': '!!REMOVE THIS EXAMPLE ROW!!',
    'city': 'New York City',
    'state': 'NY',
    'work_type': 'ONE OF: %s' % ', '.join(site_db.Site.work_type.choices),
}

for field_name, field_type in FIELD_TYPES.items():
    example_value = {
        BooleanProperty: 'yes',
        IntegerProperty: '0',
        FloatProperty: '0.0',
        DateTimeProperty: '28/2/2013'
    }.get(field_type, None)
    if example_value:
        EXAMPLE_DATA[field_name] = example_value

#
# define CSV template rows
#

HEADINGS_ROW = FIELD_NAMES
EXAMPLES_ROW = [EXAMPLE_DATA.get(name, '') for name in FIELD_NAMES]


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
    elif field_type == IntegerProperty:
        return int(field_value)
    elif field_type == FloatProperty:
        return float(field_value)
    elif field_type == BooleanProperty:
        if field_value.lower() in TRUE_VALUES:
            return True
        elif field_value.lower() in FALSE_VALUES:
            return False
        else:
            return field_value # handle error later
    elif field_type == DateTimeProperty:
        try:
            return parse_date(field_value, dayfirst=False) # assume American format
        except ValueError:
            return field_value # handle error later
    elif field_type == ReferenceProperty:
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
                d[field_name] = results[0]
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
        return validation
    else:
        validation['row_length_ok'] = True

    # validate does not contain example data
    row_d = row_to_dict(event, FIELD_NAMES, row)
    validation['contains_example_data'] = any(
        'example' in val.lower() for val in row_d.values() if isinstance(val, basestring)
    )
    if validation['contains_example_data']:
        return validation

    # validate specifically required fields (as form_handler does)
    for field_name in ADDITIONALLY_REQUIRED_FIELDS:
        if field_name not in row_d:
            validation['missing_fields'].append(field_name)
    if validation['missing_fields']:
        return validation

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
            site = site_db.Site(**validation_row_copy)
            if error_encountered:
                return validation
            else:
                break
        except BadValueError, e:
            field_name = e.message.split(' ')[1]
            if field_name in validation:
                return validation
            validation['invalid_fields'][field_name] = e.message
            del(validation_row_copy[field_name])
            error_encountered = True

    # bail out if any errors so far
    v = validation
    if any((not v['row_length_ok'], v['invalid_fields'], v['missing_fields'])):
        return validation

    # validate full address by geocoding
    full_address = ', '.join(
        filter(None, [
            row_d.get(name, None) for name in ['address', 'city', 'state']
        ])
    )
    geocode_result = google_maps_utils.geocode(full_address)
    validation['address_geocodes_ok'] = bool(geocode_result)
    if not validation['address_geocodes_ok']:
        return validation

    # fully validated
    validation['validates'] = True
    return validation

def validation_to_text(validation):
    """
    Return readable description of @validation.
    """
    s = ""
    if not validation['row_length_ok']:
        s += "Row is incorrect length; "
    if validation['contains_example_data']:
        s += "Row contains example data; "
    if validation['missing_fields']:
        s += "Missing fields: %s; " % ', '.join(validation['missing_fields'])
    if validation['invalid_fields']:
        s += "Invalid fields: %s; " % ', '.join(validation['invalid_fields'])
    if not s and not validation['address_geocodes_ok']:
        s += "Could not find address; "
    return "ERRORS: %s" % s

class HeaderException(Exception): pass

def read_csv(event, fd):
    """
    Read CSV @fd to dictionary of annotated rows.
    """
    reader = UnicodeReader(fd)
    output = {'rows': []}
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
                    output['field_names'] = row
                    continue
        else:
            validation = validate_row(event, row)
            row_dict = row_to_dict(event, FIELD_NAMES, row)
            output['rows'].append({
                'num': row_num,
                'row': row,
                'row_dict': row_dict,
                'validation': validation,
            })
    return output

def write_csv(fd, rows):
    writer = UnicodeWriter(fd)
    writer.writerow(HEADINGS_ROW)
    for row in rows:
        writer.writerow(row)

#
# templates
#

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

    # return upload form
    events_list = db.GqlQuery("SELECT * FROM Event ORDER BY created_date DESC")
    self.response.out.write(import_template.render({
        'global_admin': global_admin,
        'events_list': events_list,
        'valid_work_types': site_db.Site.work_type.choices,
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

    # get params
    action = self.request.get('action')
    blob_key = self.request.get('blob_key')
    event_id = self.request.get('choose_event')
    if not event_id:
      self.response.out.write('No event selected.')
      return
    event = event_db.GetEventFromParam(event_id)

    # no action => upload & analyse CSV
    if not action:
      # get param
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

      # analyse csv   
      blob_fd = blobstore.BlobReader(blob_key)
      try:
        csv_dict = read_csv(event, blob_fd)
      except HeaderException, e:
        self.response.out.write('Exception: ' + str(e))
        return
      field_names = csv_dict['field_names']
      annotated_rows = csv_dict['rows']
      valid_row_count = len(
          filter(None, 
            [row for row in annotated_rows if row['validation'].get('validates', None)]
          )
      )
      invalid_row_count = len(annotated_rows) - valid_row_count
      self.response.out.write(check_template.render({
          'global_admin': global_admin,
          'event': event,
          'form': site_db.SiteForm(),
          'field_names': field_names,
          'annotated_rows': annotated_rows,
          'valid_row_count': valid_row_count,
          'invalid_row_count': invalid_row_count,
          'blob_key': blob_key,
      }))
      return

    # action write valid rows
    if action == 'write':
      blob_fd = blobstore.BlobReader(blob_key)
      csv_dict = read_csv(event, blob_fd)
      sites_written = 0
      for row in csv_dict['rows']:
        if row['validation'].get('validates', False):
          row_dict = row['row_dict']
          new_site = site_db.Site(**row_dict)
          new_site.event = event
          new_site.save()
          sites_written += 1
      self.response.out.write('Saved %d new site(s).' % sites_written)
      return

    # action download invalid CSV
    if action == 'download_invalid_csv':
      blob_fd = blobstore.BlobReader(blob_key)
      csv_dict = read_csv(event, blob_fd)
      warning_row = [
        'WARNING: error messages', 'have been added',
        'at the far right', 'of each row. ',
        'Remove them', 'and this row', 'before resubmitting.'
      ]
      rows_for_csv = [warning_row] + [
        row['row'] + [validation_to_text(row['validation'])]
        for row in csv_dict['rows'] if not row['validation'].get('validates', False)
      ]
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
