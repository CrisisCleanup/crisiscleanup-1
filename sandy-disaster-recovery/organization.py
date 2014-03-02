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

import wtforms
from wtforms.ext.appengine.db import model_form
from wtforms import TextField, validators, SelectField, DateTimeField, BooleanField
from google.appengine.api import memcache
from google.appengine.ext.db import Key, to_dict

import primary_contact_db
import event_db
import cache
from form_utils import MultiCheckboxField


class Organization(db.Expando):
  """ Data about the organization. """

  name = db.StringProperty(required = True)

  # We store passwords in plain text, because we want to
  # set the passwords ourselves, and may need to be able
  # to retrieve them for an organization.
  password = db.StringProperty()

  # If set, then only session cookies are sent to the
  # user's browser. Otherwise, they'll receive cookies that
  # will expire in 1 week.
  only_session_authentication = db.BooleanProperty(default = True)

  org_verified = db.BooleanProperty(required=False)
  is_active = db.BooleanProperty(default=False)
  is_admin = db.BooleanProperty(default=False)
  deprecated = db.BooleanProperty(default=False)
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
  _incident_legacy = db.ReferenceProperty(name='incident')
  _incidents_keys = db.ListProperty(db.Key, name='incidents')
  publish = db.BooleanProperty(required=False)

  does_recovery = db.BooleanProperty(required=False)
  does_only_coordination = db.BooleanProperty(required=False)
  does_only_sit_aware = db.BooleanProperty(required=False) # situational awareness
  does_something_else = db.BooleanProperty(required=False)
  not_an_org = db.BooleanProperty(required=False)
  reputable = db.BooleanProperty(required=False)
  physical_presence = db.BooleanProperty(required=False)#|Does your Organization have a physical presence in the disaster area?

  work_area = db.StringProperty(required=False)#|If so, in which areas are you primarily working?

  # note: voad_referral is used for any kind of referral
  voad_referral = db.TextProperty(required=False)#|If your organization is not a member of VOAD, please provide the name and contact information for at least one (and preferably three or more) representatives from VOAD organizations or a government agency who can vouch for your work: # - not necessarily VOAD referral

  admin_notes = db.TextProperty(required=False)
  
  # timestamps
  timestamp_signup = db.DateTimeProperty(required=False, auto_now=True)#|Signed Up (Not Displayed)
  timestamp_login = db.DateTimeProperty(required=False)
  permissions = db.StringProperty(required=False, default="Full Access")

  # automatically deferencing incidents field

  def _get_incidents(self):
      # temporary auto-migration: copy individual incident to incidents list
      if self._incident_legacy and not self._incidents_keys:
          self._incidents_keys = [self._incident_legacy.key()]
          self.save()

      return [event_db.Event.get(incident) for incident in self._incidents_keys]

  def _set_incidents(self, incidents):
      if all(type(inc) == event_db.Event for inc in incidents):
          self._incidents_keys = [inc.key() for inc in incidents]
      elif all(type(inc) == Key for inc in incidents):
          self._incidents_keys = incidents  # TODO could check type of Key's ref
      else:
          raise Exception("incidents not of allowed type")

  def _del_incidents(self):
      del(self._incidents_keys)

  incidents = property(_get_incidents, _set_incidents, _del_incidents)


  # access controls

  @property
  def is_global_admin(self):
      return self.name == "Admin"

  @property
  def is_local_admin(self):
      return self.is_admin and not self.is_global_admin

  def join(self, event):
      assert type(event) is event_db.Event
      if event.key() not in self._incidents_keys:
          self.incidents = self.incidents + [event]

  def may_access(self, obj):
      if type(obj) is event_db.Event:
          return self.is_global_admin or obj.key() in self._incidents_keys
      else:
          raise NotImplementedError("may_access(obj) of type %s" % type(obj))

  def may_administer(self, org_or_contact):
      " Returns true if self may administer org/contact. "
      # get org to check against
      if type(org_or_contact) is Organization:
          org = org_or_contact
      elif type(org_or_contact) is primary_contact_db.Contact:
          org = org_or_contact.organization
      else:
          raise Exception("org_or_contact is of unexpected type %s" % type(org_or_contact))

      # check authority
      return (
          self.is_global_admin or
          self.is_local_admin and any(
              incident.key() in [self_incident.key() for self_incident in self.incidents]
              for incident in org.incidents
          )
      )

  @property
  def contacts(self):
      return primary_contact_db.Contact.gql(
          "WHERE organization = :1", self.key()
      )

  @property
  def primary_contacts(self):
    return primary_contact_db.Contact.gql(
      "WHERE organization = :1 and is_primary = True",
      self.key()
    )

  def __repr__(self):
      return u"<Organization: %s>" % self.name

  
cache_prefix = Organization.__name__ + "-d:"
  
ten_minutes = 600


def GetCached(org_id):
  return cache.GetCachedById(Organization, ten_minutes, org_id)


def GetAndCache(org_id):
  return cache.GetAndCache(Organization, ten_minutes, org_id)


def GetAllCached():
  return cache.GetAllCachedBy(Organization, ten_minutes)

  
def OrgToDict(organization):
    org_dict = to_dict(organization)
    org_dict["id"] = organization.key().id()
    return org_dict


def PutAndCache(organization, cache_time):
    organization.put()
    return memcache.set(cache_prefix + str(organization.key().id()),
    (organization, OrgToDict(organization)),
    time = cache_time)


@db.transactional(xg=True)
def PutAndCacheOrganizationAndContact(organization, contact_or_contacts):
    PutAndCache(organization, ten_minutes)

    # handle one or more contacts
    try:
        contacts = iter(contact_or_contacts)
    except TypeError:
        contacts = [contact_or_contacts]
    for contact in contacts:
        contact.organization=organization.key()
        primary_contact_db.PutAndCache(contact, ten_minutes)


class OrganizationAdminForm(model_form(Organization)):
    # TODO: replace with a sub-class of a newer model form
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


class OrganizationValidatorsMixIn(object):
    """ Seperated because validation may not be required. """
    name = TextField(
        'Organization Name',[
            wtforms.validators.Length(
                min=1, max=100,
                message = "Organization Name must be between 1 and 100 characters"
            )
        ]
    )
    email = TextField(
        'Organization Email', [
            wtforms.validators.Length(
                min=1, max=100,
                message = "Name must be between 1 and 100 characters"
            ),
            wtforms.validators.Email(
                message="That's not a valid email address."
            )
        ]
    )
    phone = TextField(
        'Organization Phone Number', [
            wtforms.validators.Length(
                min=1, max=100,
                message = "Organization phone must be between 1 and 100 characters")
        ]
    )
    url = TextField(
        'Organization URL', [
            wtforms.validators.Length(
                min=0, max=100,
                message = "Organization URL must be between 0 and 100 characters"
            )
        ]
    )
    twitter = TextField(
        'Organization Twitter', [
            wtforms.validators.Length(
                min=0, max=16,
                message = "Twitter handle must be between 0 and 16 characters")
        ]
    )
    facebook = TextField(
        'Facebook Link', [
            wtforms.validators.Length(
                min=0, max=100,
                message = "Facebook link must be between 0 and 100 characters")
        ]
    )


def event_key_coerce(x):
    if type(x) is event_db.Event:
        return x.key()
    elif type(x) is Key:
        return x
    else:
        return Key(x)


class OrganizationForm(
        model_form(
            Organization,
            exclude=['incidents', 'is_admin', 'timestamp_signup', 'timestamp_login', 'permissions']
        ),
        OrganizationValidatorsMixIn
    ): 
    """ All fields available to all levels of admin. """

    incidents = MultiCheckboxField(
        choices=[(event.key(), event.name) for event in event_db.Event.all()],
        coerce=event_key_coerce,
    )
    
    permissions = SelectField(u'Permission', choices=[('Full Access', 'Full Access'), ('Partial Access', 'Partial Access'), ('Situational Awareness', 'Situational Awareness')])
    timestamp_login = DateTimeField(
        "Last logged in",
        [validators.optional()]
    )

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)

        # override incidents data
        incidents = kwargs.get('incidents')
        if incidents is not None:
            self.incidents.data = incidents


class GlobalAdminOrganizationForm(OrganizationForm):

    is_admin = BooleanField()


class CreateOrganizationForm(OrganizationForm):

    incident = SelectField()  # choices to be dynamically set


class GlobalAdminCreateOrganizationForm(GlobalAdminOrganizationForm):

    incident = SelectField()  # choices to be dynamically set


class OrganizationInformationForm(
        model_form(
            Organization,
            only=[
                'name', 'email', 'phone', 'url', 'twitter', 'facebook',
                'address', 'city', 'state', 'zip_code', 'publish'
            ]
        ),
        OrganizationValidatorsMixIn
    ):
    """ For editing of org by non-admin user. """
    pass
