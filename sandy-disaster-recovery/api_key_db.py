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

from google.appengine.ext import db


class ApiKey(db.Model):
    name = db.StringProperty(required=True)
    value = db.StringProperty(required=True)


def get_api_key(name):
    try:
        return ApiKey.all().filter('name', name)[0].value
    except:
        raise Exception("API key %s not defined" % name)


# create dummy entry on module load
if ApiKey.all().count() == 0:
    ApiKey(name='dummy', value='dummy').save()
