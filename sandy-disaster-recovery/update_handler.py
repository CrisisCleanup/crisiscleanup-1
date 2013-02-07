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
import webapp2
from google.appengine.ext import deferred

# Local libraries.
import base
import update_schema



class UpdateHandler(base.AuthenticatedHandler):
    def AuthenticatedGet(self, org, event):
        if not org.name == "Administrator":
            return False  
        update_schema.UpdateSchema(self, event)
        
        