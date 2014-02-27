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
# System libraries.
import jinja2
import os
import webapp2_extras
from datetime import datetime
from google.appengine.ext import db

# Local libraries.
import base
import key
from models import incident_definition

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname( __file__ ), '..', 'templates/html/default/')))
template = jinja_environment.get_template('/incident_definition.html')

read_template = jinja_environment.get_template('/incident_definition_read.html')

CASE_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

def make_date_object(date_string):
  pass

class IncidentDefinition(base.RequestHandler):
  def get(self):
    id = self.request.get("id")
    if id:
      incident_definition_object = incident_definition.IncidentDefinition.get_by_id(int(id))
      data = {
	"incident_definition_object": incident_definition_object,
      }
      self.response.out.write(read_template.render(data))
    else:
      work_order_prefix = "Set from event_db"
      query_string = "SELECT * FROM Event"
      events_list = db.GqlQuery(query_string)
      count = events_list.count()
      current_date = None
      data = {
	"work_order_prefix": CASE_LABELS[count],
	"current_date": current_date,
      }
      self.response.out.write(template.render(data))

  def post(self):
    incident_version = self.request.get("incident_version")
    incident_full_name = self.request.get("incident_full_name")
    incident_short_name = self.request.get("incident_short_name")
    timezone = self.request.get("timezone")
    incident_date = self.request.get("incident_date")
    start_date = self.request.get("incident_start_date")
    end_date = self.request.get("incident_end_date")
    work_order_prefix = self.request.get("work_order_prefix")
    centroid_latitude = self.request.get("centroid_latitude")
    centroid_longitude = self.request.get("centroid_longitude")
    camera_latitude = self.request.get("camera_latitude")
    camera_longitude = self.request.get("camera_longitude")
    developer_mode = bool(self.request.get("developer_mode"))
    ignore_validation = bool(self.request.get("ignore_validation"))
    
    local_admin_name = self.request.get("local_admin_name")
    local_admin_title = self.request.get("local_admin_title")
    local_admin_organization = self.request.get("local_admin_organization")
    local_admin_email = self.request.get("local_admin_email")
    local_admin_cell_phone = self.request.get("local_admin_cell_phone")
    local_admin_password = self.request.get("local_admin_password")
  
  
    public_map_title = self.request.get("public_map_title")
    public_map_url = self.request.get("public_map_url")
    public_map_cluster = bool(self.request.get("public_map_cluster"))
    public_map_zoom = self.request.get("public_map_zoom")
    
    internal_map_title = self.request.get("internal_map_title")
    internal_map_url = self.request.get("internal_map_url")
    internal_map_cluster = bool(self.request.get("internal_map_cluster"))
    internal_map_zoom = self.request.get("internal_map_zoom")
  
    start_date_object = datetime.strptime(start_date, "%m/%d/%Y").date()
    end_date_object = datetime.strptime(end_date, "%m/%d/%Y").date()
    incident_date_object = datetime.strptime(incident_date, "%m/%d/%Y").date()

    inc_def = incident_definition.IncidentDefinition(version = incident_version, full_name = incident_full_name, short_name = incident_short_name, timezone = timezone, start_date = start_date_object, end_date = end_date_object, incident_date = incident_date_object, work_order_prefix = work_order_prefix, centroid_lat = centroid_latitude, centroid_lng = centroid_longitude, camera_latitude = camera_latitude, camera_longitude = camera_longitude, developer_mode = developer_mode, ignore_validation = ignore_validation, local_admin_name = local_admin_name, local_admin_title = local_admin_title, local_admin_organization = local_admin_organization, local_admin_email = local_admin_email, local_admin_cell_phone = local_admin_cell_phone, local_admin_password = local_admin_password, public_map_cluster = public_map_cluster, public_map_title = public_map_title, public_map_url = public_map_url, public_map_zoom = public_map_zoom, internal_map_cluster = internal_map_cluster, internal_map_title = internal_map_title, internal_map_url = internal_map_url, internal_map_zoom = internal_map_zoom)
    inc_def.put()
    
    self.redirect("/incident_definition?id=" + str(inc_def.key().id()))

    
  
    # make dates date objects
    # use make_date_object
    
    
    
    #hash a password
    #webapp2_extras.security.hash_password(password, method, salt=None, pepper=None)
    #get password hash
    #webapp2_extras.security.check_password_hash(password, pwhash, pepper=None)
    
