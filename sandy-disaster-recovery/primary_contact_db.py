#!/usr/bin/env python
#
# Copyright 2012 Andy Gimma
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
import wtforms.ext.dateutil.fields
import wtforms.fields
from google.appengine.ext.db import to_dict
from google.appengine.ext import db
from wtforms.ext.appengine.db import model_form
from google.appengine.api import memcache
import json
from google.appengine.ext.db import Query

from wtforms import Form, BooleanField, TextField, validators, PasswordField, ValidationError, RadioField, SelectField

# Local libraries.
import cache




class Contact(db.Model):
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    phone = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    organization = db.ReferenceProperty()
    is_primary = db.BooleanProperty()
    
cache_prefix = Contact.__name__ + "-d:"
    
def PutAndCache(contact, cache_time):
    contact.put()
    return memcache.set(cache_prefix + str(contact.key().id()),
    (contact, ContactToDict(contact)),
    time = cache_time)
        
  
def GetAllCached():
    pass

def GetAndCache(contact_id):
    contact = Contact.get_by_id(contact_id)
    if contact:
        memcache.set(cache_prefix + str(contact.key().id()),
        (contact, ContactToDict(contact)),
        time = cache_time)
        return contact

def ContactToDict(contact):
  contact_dict = to_dict(contact)
  contact_dict["id"] = contact.key().id()
  return contact_dict
  
def RemoveOrgFromContacts(org):
    contacts = db.GqlQuery("SELECT * From Contact WHERE organization = :1", org.key())
    to_put = []
    for c in contacts:
        c.organization = None
        to_put.append(c)
    if to_put:
        db.put(to_put)
        
    
    # search all contacts with -org- as incident
    # set incident to None
    # putandcache
    
class ContactForm(model_form(Contact)):
    first_name = TextField('First Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    last_name = TextField('Last Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    phone = TextField('Phone', [wtforms.validators.Length(min = 1, max = 15,
    message = "Phone must be between 1 and 15 characters")])
    email = TextField('Email', [wtforms.validators.Length(min = 1, max = 100,
    message = "Email must be between 1 and 100 characters"), validators.Email(message="That's not a valid email address.")])
    
class ContactFormFull(model_form(Contact)):
    first_name = TextField('First Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    last_name = TextField('Last Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    phone = TextField('Phone', [wtforms.validators.Length(min = 1, max = 15,
    message = "Phone must be between 1 and 15 characters")])
    email = TextField('Email', [wtforms.validators.Length(min = 1, max = 100,
    message = "Email must be between 1 and 100 characters"), validators.Email(message="That's not a valid email address.")])
    is_primary = RadioField(
    choices = [(1, "True"), (0, "False")],
    coerce = int)
    