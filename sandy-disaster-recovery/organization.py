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
from google.appengine.ext import db

import cache
from wtforms.ext.appengine.db import model_form
from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField
import wtforms
import random_password
from google.appengine.api import memcache
from google.appengine.ext.db import to_dict
import primary_contact_db

class Organization(db.Model):
  # Data about the organization.
  name = db.StringProperty(required = True)
  # We store passwords in plain text, because we want to
  # set the passwords ourselves, and may need to be able
  # to retrieve them for an organization.
  password = db.StringProperty(default=random_password.generate_password())
  primary_contact_email = db.StringProperty(default = '') # DEPRECATED - to be removed
  # If set, then only session cookies are sent to the
  # user's browser. Otherwise, they'll receive cookies that
  # will expire in 1 week.
  only_session_authentication = db.BooleanProperty(default = True)
  org_verified = db.BooleanProperty(required=False)
  is_active = db.BooleanProperty(default=False)
  is_admin = db.BooleanProperty(default=False)
  #name = db.StringProperty(required=True)
  address = db.StringProperty(required=False)
  city = db.StringProperty(required=False)
  state = db.StringProperty(required=False)
  zip_code = db.StringProperty(required=False)
  phone = db.StringProperty(required=False)
  latitude = db.FloatProperty(default = 0.0)
  longitude = db.FloatProperty(default = 0.0)
  url = db.StringProperty(required=False)
  twitter = db.StringProperty(required=False)
  facebook = db.StringProperty(required=False)
  email = db.StringProperty(required=False)
  incident = db.ReferenceProperty()
  publish = db.BooleanProperty(required=False)
  
  
  voad_referral = db.TextProperty(required=False)#|If your organization is not a member of VOAD, please provide the name and contact information for at least one (and preferably three or more) representatives from VOAD organizations or a government agency who can vouch for your work:
  physical_presence = db.BooleanProperty(required=False)#|Does your Organization have a physical presence in the disaster area?
  work_area = db.StringProperty(required=False)#|If so, in which areas are you primarily working?
  number_volunteers = db.StringProperty(required=False)#|Approximately how many volunteers will your organization utilize for cleanup efforts?
  voad_member = db.BooleanProperty(required=False)#|Is your organization a member of National VOAD, a State VOAD or County VOAD/COAD?
  voad_member_url = db.TextProperty(required=False)#|If so, can you provide one or more URLs listing your organizations membership? (This will significantly speed up approval)
  
  
  # PHASES. Note: Phases attach to an incident, not an organization. An organization may complete different phases, depending upon the incident.
  # Setting defaults to True for schema update. Otherwise all old organizations will have no phases in scope
  canvass = db.BooleanProperty(required=False, default=True)#|Canvass
  assessment = db.BooleanProperty(required=False, default=True)#|Assessment
  clean_up = db.BooleanProperty(required=False, default=True)#|Clean-up
  water_pumping = db.BooleanProperty(required=False, default=True)#|Water Pumping
  muck_out = db.BooleanProperty(required=False, default=True)#|Muck Out
  interior_debris = db.BooleanProperty(required=False, default=True)#|Interior Debris
  gutting = db.BooleanProperty(required=False, default=True)#|Gutting
  tree_removal = db.BooleanProperty(required=False, default=True)#|Tree Removal
  exterior_debris = db.BooleanProperty(required=False, default=True)#|Exterior Debris
  sanitizing = db.BooleanProperty(required=False, default=True)#|Sanitizing
  mold_treatment = db.BooleanProperty(required=False, default=True)#|Mold Treatment
  design = db.BooleanProperty(required=False, default=True)#|Design
  permits = db.BooleanProperty(required=False, default=True)#|Building Permits
  reconstruction = db.BooleanProperty(required=False, default=True)#|Reconstruction
  replace_appliances = db.BooleanProperty(required=False, default=True)#|Replace Appliances
  replace_furniture = db.BooleanProperty(required=False, default=True)#|Replace Furniture
  mold_abatement = db.BooleanProperty(required=False, default=True)#|Mold Abatement
  refurbishing = db.BooleanProperty(required=False, default=True)#|Refurbishing

  _ACTIVE_PHASE_BOOLEANS = [
    canvass,
    assessment,
    water_pumping,
    muck_out,
    interior_debris,
    gutting,
    tree_removal,
    exterior_debris,
    sanitizing,
    mold_treatment,
    design,
    permits,
    reconstruction,
    replace_appliances,
    replace_furniture
  ]

  def get_phase_boolean_names(self):
      return [pb.name for pb in self._ACTIVE_PHASE_BOOLEANS]

  #OTHER
  timestamp_signup = db.DateTimeProperty(required=False, auto_now=True)#|Signed Up (Not Displayed)
  
cache_prefix = Organization.__name__ + "-d:"
  
ten_minutes = 600
def GetCached(org_id):
  return cache.GetCachedById(Organization, ten_minutes, org_id)

def GetAndCache(org_id):
  return cache.GetAndCache(Organization, ten_minutes, org_id)

def GetAllCached():
  return cache.GetAllCachedBy(Organization, ten_minutes)

  
def GetAllContactsByOrgId(org_id):
    organization = Organization.get_by_id(org)    
    return Contact.gql("WHERE organizations = :1", organization.key())
 
def OrgToDict(organization):
    org_dict = to_dict(organization)
    org_dict["id"] = organization.key().id()
    return org_dict
    
def PutAndCache(organization, cache_time):
    organization.put()
    return memcache.set(cache_prefix + str(organization.key().id()),
    (organization, OrgToDict(organization)),
    time = cache_time)

ten_minutes = 600    
@db.transactional(xg=True)
def PutAndCacheOrganizationAndContact(organization, contact):
    PutAndCache(organization, ten_minutes)
    contact.organization=organization.key()
    primary_contact_db.PutAndCache(contact, ten_minutes)


class OrganizationAdminForm(model_form(Organization)):
    contact_first_name = TextField('First Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your name must be between 1 and 100 characters")])
                              
    contact_last_name = TextField('Last Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your name must be between 1 and 100 characters")])
    contact_email = TextField('Your Email', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your email must be between 1 and 100 characters"),
                              validators.Email(message="That's not a valid email address.")])
    contact_phone = TextField('Your Phone Number', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your phone must be between 1 and 100 characters")])
    name = TextField('Organization Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Organization Name must be between 1 and 100 characters")])
    email = TextField('Organization Email', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Name must be between 1 and 100 characters"),
                              validators.Email(message="That's not a valid email address.")])
    phone = TextField('Organization Phone Number', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Organization phone must be between 1 and 100 characters")])
    address = TextField('Address')
    city = TextField('City')
    state = TextField('State')
    zip_code = TextField('Zip Code')
    url = TextField('Organization URL', [wtforms.validators.Length(min = 0, max = 100,
                              message = "Organization URL must be between 0 and 100 characters")])
    twitter = TextField('Organization Twitter', [wtforms.validators.Length(min = 0, max = 16,
                              message = "Twitter handle must be between 0 and 16 characters")])
    facebook = TextField('Facebook link', [wtforms.validators.Length(min = 0, max = 100,
                              message = "Facebook link must be between 0 and 100 characters")])

def coerce_int_str_to_bool(x):
    """
    >>> coerce_int_str_to_bool(1)
    True
    >>> coerce_int_str_to_bool("1")
    True
    >>> coerce_int_str_to_bool(0)
    False
    >>> coerce_int_str_to_bool("0")
    False
    """
    if isinstance(x, int):
        return bool(x)
    elif isinstance(x, basestring):
        return bool(int(x))

def always_often_rarely_never(label):
    return RadioField(
      label,
      choices=[(1, "Always/Often"), (0, "Rarely/Never")],
      coerce=coerce_int_str_to_bool,
    )

class OrganizationPhaseBooleanMixin(Form):
    canvass = always_often_rarely_never('Canvass')
    assessment = always_often_rarely_never('Assessment')
    water_pumping = always_often_rarely_never('Water Pumping')
    muck_out = always_often_rarely_never('Muck Out')
    interior_debris = always_often_rarely_never('Interior Debris')
    gutting = always_often_rarely_never('Gutting')
    tree_removal = always_often_rarely_never('Tree Removal')
    exterior_debris = always_often_rarely_never('Exterior Debris')
    sanitizing = always_often_rarely_never('Sanitizing')
    mold_treatment = always_often_rarely_never('Mold Treatment')
    design = always_often_rarely_never('Design')
    permits = always_often_rarely_never('Permits')
    reconstruction = always_often_rarely_never('Reconstruction')
    replace_appliances = always_often_rarely_never('Replace Appliances')
    replace_furniture = always_often_rarely_never('Replace Furniture')

    def get_phase_fields(self):
        return [
            self.canvass,
            self.assessment,
            self.water_pumping,
            self.muck_out,
            self.interior_debris,
            self.gutting,
            self.tree_removal,
            self.exterior_debris,
            self.sanitizing,
            self.mold_treatment,
            self.design,
            self.permits,
            self.reconstruction,
            self.replace_appliances,
            self.replace_furniture
        ]


class OrganizationFormNoContact(OrganizationPhaseBooleanMixin, model_form(Organization)):
    name = TextField('Organization Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization Name must be between 1 and 100 characters")])
    email = TextField('Organization Email', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters"),
    validators.Email(message="That's not a valid email address.")])
    phone = TextField('Organization Phone Number', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization phone must be between 1 and 100 characters")])
    address = TextField('Address')
    city = TextField('City')
    state = TextField('State')
    zip_code = TextField('Zip Code')
    url = TextField('Organization URL', [wtforms.validators.Length(min = 0, max = 100,
    message = "Organization URL must be between 0 and 100 characters")])
    twitter = TextField('Organization Twitter', [wtforms.validators.Length(min = 0, max = 16,
    message = "Twitter handle must be between 0 and 16 characters")])
    facebook = TextField('Facebook link', [wtforms.validators.Length(min = 0, max = 100,
    message = "Facebook link must be between 0 and 100 characters")])
    
    publish = BooleanField("Publish Organization Profile")
    physical_presence = RadioField("Does your organization have a physical presence in the affected area?",
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    work_area = TextField('If so, in which areas are you primarily working?', [wtforms.validators.Length(min = 0, max = 500,
    message = "Name must be between 0 and 500 characters")])
    number_volunteers = TextField('What is your approximate number of volunteers?')
    voad_member = RadioField('Is your organization a member of National VOAD, a State VOAD or County VOAD/COAD?',
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    voad_member_url = TextField("If so, can you provide one or more URLs listing your organization's membership? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Membership urls must be between 0 and 100 characters")])
    voad_referral= TextField("If you are not a national voad, can you provide the name of a voad that will vouch for you? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Referral urls must be between 0 and 100 characters")])
    choose_event = TextField('Choose', [validators.Required()])
    
class OrganizationForm(OrganizationPhaseBooleanMixin, model_form(Organization)):
    contact_first_name = TextField('Your First Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your first name must be between 1 and 100 characters")])
    contact_last_name = TextField('Your Last Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your last name must be between 1 and 100 characters")])
    contact_email = TextField('Your Email', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your email must be between 1 and 100 characters"),
                              validators.Email(message="That's not a valid email address.")])
    contact_phone = TextField('Your Phone Number', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Your phone must be between 1 and 100 characters")])
    name = TextField('Organization Name', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Organization Name must be between 1 and 100 characters")])
    email = TextField('Organization Email', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Name must be between 1 and 100 characters"),
                              validators.Email(message="That's not a valid email address.")])
    phone = TextField('Organization Phone Number', [wtforms.validators.Length(min = 1, max = 100,
                              message = "Organization phone must be between 1 and 100 characters")])
    address = TextField('Address')
    city = TextField('City')
    state = TextField('State')
    zip_code = TextField('Zip Code')
    url = TextField('Organization URL', [wtforms.validators.Length(min = 0, max = 100,
                              message = "Organization URL must be between 0 and 100 characters")])
    twitter = TextField('Organization Twitter', [wtforms.validators.Length(min = 0, max = 16,
                              message = "Twitter handle must be between 0 and 16 characters")])
    facebook = TextField('Facebook link', [wtforms.validators.Length(min = 0, max = 100,
                              message = "Facebook link must be between 0 and 100 characters")])
                             
                             
    publish = BooleanField("Publish Organization Profile")
    physical_presence = RadioField("Does your organization have a physical presence in the affected area?",
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    work_area = TextField('If so, in which areas are you primarily working?', [wtforms.validators.Length(min = 0, max = 500,
                             message = "Name must be between 0 and 500 characters")])
    number_volunteers = TextField('What is your approximate number of volunteers?')
    voad_member = RadioField('Is your organization a member of National VOAD, a State VOAD or County VOAD/COAD?',
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    voad_member_url = TextField("If so, can you provide one or more URLs listing your organization's membership? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
                             message = "Voad Membership urls must be between 0 and 100 characters")])
    voad_referral= TextField("If you are not a national voad, can you provide the name of a voad that will vouch for you? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
                             message = "Voad Referral urls must be between 0 and 100 characters")])

    choose_event = TextField('Choose', [validators.Required()])
   

class OrganizationEditForm(OrganizationPhaseBooleanMixin, model_form(Organization)):
    name = TextField('Organization Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization Name must be between 1 and 100 characters")])
    password = TextField('Organization Password', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization password must be between 1 and 100 characters")])
    email = TextField('Organization Email', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters"),
    validators.Email(message="That's not a valid email address.")])
    phone = TextField('Organization Phone Number', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization phone must be between 1 and 100 characters")])
    address = TextField('Address')
    city = TextField('City')
    state = TextField('State')
    zip_code = TextField('Zip Code')
    url = TextField('Organization URL', [wtforms.validators.Length(min = 0, max = 100,
    message = "Organization URL must be between 0 and 100 characters")])
    twitter = TextField('Organization Twitter', [wtforms.validators.Length(min = 0, max = 16,
    message = "Twitter handle must be between 0 and 16 characters")])
    facebook = TextField('Facebook link', [wtforms.validators.Length(min = 0, max = 100,
    message = "Facebook link must be between 0 and 100 characters")])
    
    
    publish = BooleanField("Publish Organization Profile")
    physical_presence = RadioField("Does your organization have a physical presence in the affected area?",
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    work_area = TextField('If so, in which areas are you primarily working?', [wtforms.validators.Length(min = 0, max = 500,
    message = "Name must be between 0 and 500 characters")])
    number_volunteers = TextField('What is your approximate number of volunteers?')
    voad_member = RadioField('Is your organization a member of National VOAD, a State VOAD or County VOAD/COAD?',
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    voad_member_url = TextField("If so, can you provide one or more URLs listing your organization's membership? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Membership urls must be between 0 and 100 characters")])
    voad_referral= TextField("If you are not a national voad, can you provide the name of a voad that will vouch for you? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Referral urls must be between 0 and 100 characters")])

    org_verified = RadioField(
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    is_active = RadioField(
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)

class OrganizationInfoEditForm(OrganizationPhaseBooleanMixin, model_form(Organization)):
    name = TextField('Organization Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization Name must be between 1 and 100 characters")])
    password = TextField('Organization Password', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization password must be between 1 and 100 characters")])
    email = TextField('Organization Email', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters"),
    validators.Email(message="That's not a valid email address.")])
    phone = TextField('Organization Phone Number', [wtforms.validators.Length(min = 1, max = 100,
    message = "Organization phone must be between 1 and 100 characters")])
    address = TextField('Address')
    city = TextField('City')
    state = TextField('State')
    zip_code = TextField('Zip Code')
    url = TextField('Organization URL', [wtforms.validators.Length(min = 0, max = 100,
    message = "Organization URL must be between 0 and 100 characters")])
    twitter = TextField('Organization Twitter', [wtforms.validators.Length(min = 0, max = 16,
    message = "Twitter handle must be between 0 and 16 characters")])
    facebook = TextField('Facebook link', [wtforms.validators.Length(min = 0, max = 100,
    message = "Facebook link must be between 0 and 100 characters")])
    
    publish = BooleanField("Publish Organization Profile")
    physical_presence = RadioField("Does your organization have a physical presence in the affected area?",
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    work_area = TextField('If so, in which areas are you primarily working?', [wtforms.validators.Length(min = 0, max = 500,
    message = "Name must be between 0 and 500 characters")])
    number_volunteers = TextField('What is your approximate number of volunteers?')
    voad_member = RadioField('Is your organization a member of National VOAD, a State VOAD or County VOAD/COAD?',
    choices = [(1, "Yes"), (0, "No")],
    coerce=coerce_int_str_to_bool)
    voad_member_url = TextField("If so, can you provide one or more URLs listing your organization's membership? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Membership urls must be between 0 and 100 characters")])
    voad_referral= TextField("If you are not a national voad, can you provide the name of a voad that will vouch for you? (This will greatly speed up approval)", [wtforms.validators.Length(min = 0, max = 100,
    message = "Voad Referral urls must be between 0 and 100 characters")])

