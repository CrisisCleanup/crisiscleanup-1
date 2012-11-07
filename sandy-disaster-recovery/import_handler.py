# System libraries.

import json
import logging
from google.appengine.api.urlfetch import fetch

# Local libraries.
import base
import organization
import site_db

class ImportHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org):
    os = organization.Organization.gql("WHERE name = :1", "cheese")
    org_name = "cheese"
    orgs = [org for org in organization.Organization.gql("WHERE name = :name", name = org_name)]

    f = fetch("https://script.googleusercontent.com/echo?user_content_key=FhDerHYRqmPomvddrWG5z1EPE2M6pIsdWoneKZggh5tOOwrmP4Atbge70tQMNTIGyGqIpA2WfT2mn-b9xDGva0ig28c7dyAJm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnLQWLGh0dZkw6EUdDCIUunrCvAUHV5O19lgdOMElR3BpzsNnsNxUs69kLAqLclCCiDOmbnRGq-tk&lib=MIG37R_y3SDE8eP6TP_JVJA0rWYMbTwle");
    if f.status_code == 200:
      status_lower = [s.lower() for s in site_db.Site.status.choices]

      c = f.content.replace("var sites = ", "", 1).replace(";", "")
      all_sites = json.loads(c)
      for s in all_sites:
        self.response.write(s["Resident Name"] + "<br />")
        lookup = site_db.Site.gql("WHERE name = :name and address = :address and zip_code = :zip_code LIMIT 1",
                          name = s["Resident Name"],
                          address = s["Address"],
                          zip_code = s["Zip Code"])
        site = None
        for l in lookup:
          site = l
        # Temporary testing code
        # TODO(Jeremy): Remove this if we want to support incremental updates.
        if site:
          site.delete()
          site = None
        if not site:
          # Save the data, and redirect to the view page
          site = site_db.Site(
              address = str(s["Address"]),
              name = s["Resident Name"],
              phone1 = str(s["Contact # s (Home and Cell)"]),
              city = s["City"],
              state = s["State"],
              zip_code = str(s["Zip Code"]),
              cross_street = s["Cross Street/ Landmark"],
              time_to_call = s["Best Time to call"],
              habitable = "yes" in s["Is Home Habitable?"].lower(),
              electricity = "yes" in s["Is electricity available on site?"].lower(),
              debris_only = "yes" in s["Are you only requesting Debris removal?"].lower(),
              standing_water = "yes" in s["Standing water on site?"].lower(),
              work_requested = s["Work Requested"],
              county = s["County"],
              special_needs = s["Special Needs"],
              rent_or_own = ("Rent" if
                             "rent" in s["Own/Rent"].lower().strip()
                             else ("Own" if "own" in s["Own/Rent"].lower().strip() else None)),
              work_without_resident = "yes" in s["Work without resident present?"].lower().strip(),
              debris_removal_only = "yes" in s["Are you only requesting Debris removal?"].lower().strip(),
              electrical_lines = (
                  "yes" in s["Are there Electrical Lines in the Clean-Up Area?"].lower().strip() or
                  "yes" in s["Are there Phone or Cable Lines in the Clean-up Area"].lower().strip()),
              other_hazards = s["Any Other Hazards in the Clean-Up Area?"]
              )
        site.notes = ""
        if len(str(s["Ages of Residents"])) > 1:
          site.notes = "Age of residents: " + str(s["Ages of Residents"])
        status_str = s["Status (Do not Edit)"]
        parts = [o.strip() for o in status_str.split(':')]
        if len(parts) == 2:
          org_name = parts[0]
          status = parts[1]
          orgs = [org for org in organization.Organization.gql("WHERE name = :name", name = org_name)]
          if len(orgs):
            org = orgs[0]
            site.claimed_by = org
          if status.lower() in status_lower:
            site.status = site_db.Site.status.choices[
                status_lower.index(status.lower())]
        lls = s["Lat,  Long"].split(",")
        if len(lls) == 2:
          site.latitude = float(lls[0].strip())
          site.longitude = float(lls[1].strip())
        #logging.critical('No lat/lng: ' + site.name + " " + s["Lat,  Long"])
        site.put()
