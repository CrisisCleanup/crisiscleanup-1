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
import event_db
import organization


class NewIncident(db.Model):
    name = db.StringProperty(required=True)
    location = db.StringProperty(required=True)
    
class NewIncidentForm(model_form(NewIncident)):
    name = TextField('Name', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])
    location = TextField('Location', [wtforms.validators.Length(min = 1, max = 100,
    message = "Name must be between 1 and 100 characters")])