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


KNOWN_CONFIG_KEY_NAMES = {
    'system_email_address',
    'votesmart',
    'aws_ses_region',
    'aws_ses_access_key_id',
    'aws_ses_secret_access_key',
}


class ConfigKey(db.Model):
    name = db.StringProperty(required=True)
    value = db.StringProperty()


def get_config_key(name):
    try:
        return ConfigKey.all().filter('name', name)[0].value
    except:
        return None


# create blank config keys on module load
for known_config_key_name in KNOWN_CONFIG_KEY_NAMES:
    if ConfigKey.all().filter('name', known_config_key_name).count() == 0:
        ConfigKey(name=known_config_key_name, value=u'').save()
