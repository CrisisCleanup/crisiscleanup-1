#!/usr/bin/env python
#
# Copyright 2013 Andy Gimma
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
import logging
import wtforms.ext.dateutil.fields
import wtforms.fields
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
from google.appengine.api import memcache
import json
from google.appengine.ext.db import Query

from wtforms import Form, BooleanField, TextField, TextAreaField, validators, PasswordField, ValidationError, RadioField, SelectField
import cache

CASE_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
def get_case_label():
  work_order_prefix = "Set from event_db"
  query_string = "SELECT * FROM Event"
  events_list = db.GqlQuery(query_string)
  count = events_list.count()
  return CASE_LABELS[count]


class IncidentDefinition(db.Model):
  # TODO

  # is the next one necessary?
  #full_definition_json = db.TextProperty(required=True, default="{}")
  # should we make the next two attributes lists, rather than just json?
  phases_json = db.TextProperty(default="[]")
  # name, definition, order_number, incident reference, incident name
  forms_json = db.TextProperty(default="[]")
  # name, incident reference, incident name, attributes json
  
  # removing versions until we know what will likely be inherited
  is_version = db.BooleanProperty()
  version = db.StringProperty(required=False)
  incident = db.ReferenceProperty(required=False)
  # ensure unique
  name = db.StringProperty(required=True)
  # ensure unique
  short_name = db.StringProperty(required=False)
  # ensure unique
  timezone = db.StringProperty(required=True)
  location = db.StringProperty(required=True)
  incident_date = db.DateProperty(required=True)
  cleanup_start_date = db.DateProperty(required=True)
  cleanup_end_date = db.DateProperty(required=False)
  work_order_prefix = db.StringProperty(required=True)
  incident_lat = db.FloatProperty(required=True)
  incident_lng = db.FloatProperty(required=True)
  
  local_admin_name = db.StringProperty()
  local_admin_title = db.StringProperty()
  local_admin_organization = db.StringProperty()
  local_admin_email = db.StringProperty()
  local_admin_cell_phone = db.StringProperty()
  local_admin_password = db.StringProperty()

  public_map_title = db.StringProperty()
  public_map_url = db.StringProperty()
  public_map_cluster = db.BooleanProperty(default=True)
  public_map_zoom = db.StringProperty(default="7")
  public_map_latitude = db.FloatProperty()
  public_map_longitude = db.FloatProperty()
  
  organization_map_title = db.StringProperty()
  organization_map_url = db.StringProperty()
  organization_map_cluster = db.BooleanProperty(default=True)
  organization_map_zoom = db.StringProperty(default="7")
  organization_map_latitude = db.FloatProperty()
  organization_map_longitude = db.FloatProperty()
  
  ignore_validation = db.BooleanProperty()
  developer_mode = db.BooleanProperty()
  
  notify_unfinished = db.IntegerProperty(required=False, default=14)
  notify_on_new_orgs = db.BooleanProperty(required=False, default=False)
  notify_contacts = db.BooleanProperty(required=False, default=False)
  
class IncidentPhaseForm(Form):
  phase_name = TextField('Phase Name', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters")])
  description = TextAreaField('Description', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters")])


class AdvancedCommunicationsForm(Form):
  notify_choices_array = [
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (12, 12),
    (13, 13),
    (14, 14),
    (15, 15),
    (16, 16),
    (17, 17),
    (18, 18),
    (19, 19),
    (20, 20),
    (21, 21),
  ]
  notify_contacts = BooleanField("Notify All Contacts In Organization?", default=False)
  notify_on_new_orgs = BooleanField("Notify organizations when new organizations join?", default=False)
  notify_unfinished = wtforms.fields.SelectField("Notify when claimed sites are unchanged for", choices = notify_choices_array, coerce=int)
  
class AdvancedMapForm(Form):
  zoom_choices_array = [
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (12, 12),
  ]
  organization_map_title = TextField('Organization Map Title', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters"), wtforms.validators.Optional()])
  organization_map_url = TextField('Organization Map KML Link', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters"), wtforms.validators.Optional()])
  organization_map_latitude = TextField('Organization Map Latitude', [wtforms.validators.NumberRange(min=-90, max=90, message="Latitude must be a number between -90 and 90")])
  organization_map_longitude = TextField('Organization Map Longitude', [wtforms.validators.NumberRange(min=-180, max=180, message="Longitude must be a number between -180 and 180")])
  organization_map_cluster = BooleanField("Employ Clustering", default=False)
  organization_map_zoom = wtforms.fields.SelectField(choices = zoom_choices_array, coerce=int)

  public_map_title = TextField('Public Map Title', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters"), wtforms.validators.Optional()])
  public_map_url = TextField('Public Map KML Link', [wtforms.validators.Length(min = 1, max = 100,
      message = "Name must be between 1 and 100 characters"), wtforms.validators.Optional()])
  public_map_latitude = TextField('Public Map Latitude', [wtforms.validators.NumberRange(min=-90, max=90, message="Latitude must be a number between -90 and 90")])
  public_map_longitude = TextField('Public Map Longitude', [wtforms.validators.NumberRange(min=-180, max=180, message="Longitude must be a number between -180 and 180")])
  public_map_cluster = BooleanField("Employ Clustering", default=False)
  public_map_zoom = wtforms.fields.SelectField(choices = zoom_choices_array, coerce=int)
  
  
  
class IncidentDefinitionForm(model_form(IncidentDefinition)):
  phone_validator = wtforms.validators.Regexp(r'^\d+$', flags=0, message=u'Phone number. No letters allowed or other characters allowed.')

  name = TextField('Incident Name', [wtforms.validators.Length(min = 1, max = 100,
  message = "Name must be between 1 and 100 characters")])
  location = TextField('Location', [wtforms.validators.Length(min = 1, max = 100,
  message = "Name must be between 1 and 100 characters")])


  #short_name = TextField('Location', [wtforms.validators.Length(min = 1, max = 100,
  #message = "Name must be between 1 and 100 characters")])
  timezone = wtforms.fields.SelectField(
    choices = [("-12", "(GMT -12:00) Eniwetok, Kwajalein"), ("-11", "(GMT -11:00) Midway Island, Samoa"), ("-10", "(GMT -10:00) Hawaii"),
	       ("-9", "(GMT -9:00) Alaska"), ("-8", "Pacific Time (US and Canada)"), ("-7", "Mountain Time (US &amp; Canada)"),
	       ("-6", "Central Time (US and Canada), Mexico City"), ("-5", "Eastern Time (US and Canada), Bogota, Lima"), 
	       ("-4", "Atlantic Time (Canada), Caracas, La Paz"), ("-3.5", "Newfoundland"), ("-3", "Brazil, Buenos Aires, Georgetown"), 
	       ("-2", "Mid-Atlantic"), ("-1", "Azores, Cape Verde Islands"), ("0", "Western Europe Time, London, Lisbon, Casablanca"), 
	       ("1", "Brussels, Copenhagen, Madrid, Paris"), ("2", "Kaliningrad, South Africa"), ("3", "Baghdad, Riyadh, Moscow, St. Petersburg"),
	       ("3.5", "Tehran"), ("4", "Abu Dhabi, Muscat, Baku, Tbilisi"), ("4.5", "Kabul"), ("5", "Ekaterinburg, Islamabad, Karachi, Tashkent"),
	       ("5.75", "Kathmandu"), ("6", "Almaty, Dhaka, Colombo"), ("7", "Bangkok, Hanoi, Jakarta"), ("8", "Beijing, Perth, Singapore, Hong Kong"),
	       ("9", "Tokyo, Seoul, Osaka, Sapporo, Yakutsk"), ("9.5", "Adelaide, Darwin"), ("10", "Eastern Australia, Guam, Vladivostok"), 
	       ("11", "Magadan, Solomon Islands, New Caledonia"), ("12", "Auckland, Wellington, Fiji, Kamchatka") ],
    default = 0)
  incident_date = TextField('Incident Date (mm/dd/yyyy)', [wtforms.validators.Length(min = 1, max = 100,
  message = "Name must be between 1 and 100 characters")])
  cleanup_start_date = TextField('Cleanup Start Date (mm/dd/yyyy)', [wtforms.validators.Length(min = 1, max = 100,
  message = "Name must be between 1 and 100 characters")])
  #cleanup_end_date = TextField('Cleanup End Date (mm/dd/yyyy)')
  work_order_prefix = TextField('Work Order Prefix', default = get_case_label())
  incident_lat = TextField('Incident Latitude', [wtforms.validators.NumberRange(min=-90, max=90, message="Latitude must be a number between -90 and 90")])
  incident_lng = TextField('Incident Longitude', [wtforms.validators.NumberRange(min=-180, max=180, message="Longitude must be a number between -180 and 180")])
  #ignore_validation = BooleanField("Ignore Validation", default=False)
  #developer_mode = BooleanField("Developer Mode", default=False)
  
  local_admin_name = TextField('Local Admin Name', [wtforms.validators.Length(min = 1, max = 100,
  message = "Local Admin Name must be between 1 and 100 characters")])
  local_admin_title = TextField('Local Admin Title', [wtforms.validators.Length(min = 1, max = 100,
  message = "Local Admin Title must be between 1 and 100 characters")])
  local_admin_organization = TextField('Local Admin Organization', [wtforms.validators.Length(min = 1, max = 100,
  message = "Local Admin Organization must be between 1 and 100 characters")])
  local_admin_email = TextField('Local Admin Email', [wtforms.validators.Length(min = 1, max = 100,
  message = "Local Admin Email must be between 1 and 100 characters")])
  local_admin_cell_phone = TextField('Local Admin Cell Phone', [phone_validator])
  local_admin_password = TextField('Local Admin Password', [wtforms.validators.Regexp(r'([A-Za-z])+([0-9])+|([0-9])+([A-Za-z])+', flags=0, message=u'Password: Must contain at least one letter and at least one number')])




  #incident = ReferenceProperty()
