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
import json
import logging
from google.appengine.api.urlfetch import fetch

# Local libraries.
import base
import event_db
import organization
import site_db

class ImportHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    f = open('sheet1.csv');
    fileReader = csv.reader(f)
    firstRow = None
    all_sites = []
    for row in fileReader:
      if not firstRow:
        firstRow = row
      else:
        m = [(firstRow[i], row[i]) for i in range(len(row))]
        all_sites.append(dict(m))
    for s in all_sites:
        if s["Contact Name"] == "":
          s["Contact Name"] = "Unknown"
        self.response.write(s["Contact Name"] + "<br />")
        lookup = site_db.Site.gql("WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
                          name = s["Contact Name"],
                          address = s["Street Address"],
                          zip_code = s["Zip Code"])
        site = None
        for l in lookup:
          site = l
        def IfSet(c):
          if s[c] != "":
            return " " + c + ": " + s[c]
          return ""
        if not site:
          # Save the data, and redirect to the view page
          logging.critical(s["Contact Name"])
          site = site_db.Site(
              status = "Open, unassigned", 
              address = str(s["Street Address"]),
              name = s["Contact Name"],
              phone1 = str(s["Phone Number"]),
              county = s["County"],
              city = s["City"],
              state = s["State"],
              latitude = float(s["Latitude"]),
              longitude = float(s["Longitude"]),
              zip_code = str(s["Zip Code"]),
              notes = IfSet("Other Needs") +
              IfSet("Tools or Skills Needed") +
              IfSet("Other Information") +
              IfSet("Crew Size Needed") +
              IfSet("Estimated Length of Job") +
              IfSet("Damaged Appliance/Furniture/Flooring?") +
              IfSet("Functioning Utilities") +
              IfSet("Primary Home?") +
              IfSet("Age of Other Residents") +
              IfSet("Structural Damage to Home?") +
              IfSet("Mold Growing?") +
              IfSet("Contacted Insurance?") +
              IfSet("Water Level in Home") +
              IfSet("Contacted Landlord?") +
              IfSet("Part of House Flooded") +
              IfSet("Text") +
              IfSet("Waiting for Insurance Company?") +
              IfSet("Email") +
              IfSet("Source Name"),
              
              other_hazards = IfSet("Hazards to Look Out For") +
                  IfSet("Hazardous Materials on Property?"),
              electrical_lines = "yes" in s["Power Lines Down on Property?"].lower(),
              

              prepared_by = s["Person Reporting"],
              disabled = "yes" in s["Disabled?"].lower(),
              older_than_60 = "yes" in s["Elderly?"].lower(),
              work_requested = s["Description"] +
                  " Damage: " + s["Damage Incurred"],
              standing_water = "yes" in s["Currently Water in Home?"].lower(),
              electricity = "no" in s["Gas/Electricity Turned Off?"].lower(),
              insurance = s["Have Insurance?"])
        try:
          if len(s["Priority"]) > 0:
            site.priority = int(s["Priority"][0])
        except ValueError:
          pass
        if 'yes' in s["Homeowner?"].lower():
          site.rent_or_own = "Own"
        site.claimed_by = org
        event_db.AddSiteToEvent(site, event.key().id())
        #logging.critical('No lat/lng: ' + site.name + " " + s["Lat,  Long"])
        site_db.PutAndCache(site)
