#!/usr/bin/env python
#
# Copyright 2015 Andrew Gimma
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
import logging

# Local libraries.
import generate_hash
import organization
import datetime
import base
import audit_db


CUTOFF_DAYS = 180
FIRST_LOGIN_CUTOFF_DAYS = 30

class RemoveUnusedPasswords(base.RequestHandler):
  def get(self):
    ### Loop through the password hashes of each org
    orgs = organization.Organization.all()
    for org in orgs:
      for password_hash in org._password_hash_list:
        ### Find an audit with that password hash
        audit = audit_db.Audit.all().order("-created_at").filter("password_hash =", password_hash).get()

        ### get todays date, and set a cutoff date depending on 
        ### if the password has been used to login or not
        today = datetime.datetime.now()
        cutoff_date = today - datetime.timedelta(days=CUTOFF_DAYS)
        if audit and audit.type == "generate_new_password": 
          cutoff_date = today - datetime.timedelta(days=FIRST_LOGIN_CUTOFF_DAYS)

        ### If the password hash hasn't been used since the cutoff date
        ### try to delete it, or log the error
        if audit and audit.created_at < cutoff_date:
          try:
            org._password_hash_list.remove(password_hash)
            organization.PutAndCache(org)
            logging.info("Password removed")
          except:
            logging.error("Password removal error")
            logging.error(password_hash)
            logging.error(org.name)
