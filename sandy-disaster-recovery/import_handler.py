# System libraries.
import json
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
              )
        if len(s["Ages of Residents"]) > 1:
          site.notes += "Age of residents: " + s["Ages of Residents"]
        status_str = s["Status (Do not Edit)"]
        parts = [o.strip() for o in status_str.split(':')]
        if len(parts) == 2:
          org_name = parts[0]
          status = parts[1]
          orgs = [org for org in organization.Organization.gql("WHERE name = :name", name = org_name)]
          if len(orgs):
            org = orgs[0]
            site.claimed_by = org
          if status in site_db.STATUS_CHOICES:
            site.status = status
        if ["Lat, Long"]:
          lls = s["Lat, Long"].split(",")
          if len(lls) == 2:
            site.latitude = float(lls[0])
            site.longitude = float(lls[1])

        site.put()
