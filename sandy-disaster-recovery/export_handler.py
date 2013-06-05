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
# System libraries.
import csv

# Local libraries.
import base
import site_db
import site_util
import incident_csv_db
from google.appengine.ext import db



class ExportHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    self.AuthenticatedPost(org, event)

  def AuthenticatedPost(self, org, event):
    sites = site_util.SitesFromIds(self.request.get('id'), event)

    filename = 'work_sites.csv'
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = (
        'attachment; filename="work_sites.csv"')

    #q = db.Query(incident_csv_db.IncidentCSV)
    #q.filter("incident =", event.key())
    #query = q.get()
    #new_list = []
    
    #for i in query.incident_csv:
      #new_list.append(str(i))
      
    
    writer = csv.writer(self.response.out)
    #remove normalized, and metaphone from here.
    final_list = []
    moore_list = ["name","request_date","address","city","county","state","zip_code","cross_street","phone1","phone2","time_to_call","work_type","house_affected","outbuilding_affected","exterior_property_affected","rent_or_own","work_without_resident","member_of_assessing_organization","first_responder","older_than_60","special_needs","priority","destruction_level","house_roof_damage","outbuilding_roof_damage","tarps_needed","help_install_tarp","num_trees_down","num_wide_trees","interior_debris_removal","nonvegitative_debris_removal","vegitative_debris_removal","unsalvageable_structure","heavy_machinary_required","damaged_fence_length","fence_type","fence_notes","notes","habitable","electricity","electrical_lines","unsafe_roof","unrestrained_animals","other_hazards","status","assigned_to","initials_of_resident_present","status_notes","prepared_by","do_not_work_before"]
    
    others_list = ["name", "request_date", "address", "city", "county", "state", "zip_code", "cross_street", "phone1", "phone2", "time_to_call", "work_type", "rent_or_own", "work_without_resident", "member_of_assessing_organization", "first_responder", "older_than_60", "disabled", "priority", "flood_height", "floors_affected", "carpet_removal", "hardwood_floor_removal", "drywall_removal", "heavy_item_removal", "appliance_removal", "standing_water", "mold_remediation", "pump_needed", "num_trees_down", "num_wide_trees", "roof_damage", "tarps_needed", "debris_removal_only", "habitable", "electricity", "electrical_lines", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "prepared_by", "do_not_work_before"]
    if event.short_name == "moore":
      final_list = moore_list
    else:
      final_list = others_list
    writer.writerow(final_list)

    for site in sites:
      writer.writerow(site.ToCsvLine(final_list))