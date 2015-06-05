import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
import site_db
import event_db
from datetime import datetime
import logging

fields = ["claimed_by", "reported_by", "modified_by", "case_number", "days", "name", "request_date", "address", "city", "county", "state", "zip_code", "latitude", "longitude", "latitude_blur", "longitude_blur", "cross_street", "phone1", "phone2", "work_type", "older_than_60", "special_needs", "roof_clearing", "dig_out_car", "ice_removal", "driveway_clearing", "walkway_clearing", "stair_clearing", "ramp_clearing", "deck_clearing", "leaking", "structural_problems", "roof_collapse", "needs_food", "needs_clothing", "needs_shelter", "needs_fuel", "needs_tarp", "tree_debris", "needs_visual", "other_needs", "notes", "other_hazards", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "status_notes", "prepared_by", "do_not_work_before"]

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        process_csv(blob_info)

        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")


def process_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    blob_iterator = BlobIterator(blob_reader)
    reader = csv.reader(blob_iterator)
    count = 0
    errors = {}
    q = db.Query(event_db.Event)
    q.filter("name =", "Texas-Oklahoma Floods")
    event = q.get()
    for row in reader:
        count += 1
        if count != 1:
            logging.info(len(fields))
            logging.info(len(row))
            logging.info(row)
            #raise Exception(row)
            claimed_by,reported_by,modified_by,case_number,name,request_date,do_not_work_before,address,city,county,state,zip_code,latitude,longitude,blurred_latitude,blurred_longitude,cross_street,phone1,phone2,time_to_call,work_type,rent_or_own,work_without_resident,member_of_assessing_organization,first_responder,older_than_60,special_needs,severity,damage_notes,flood_height,floors_affected,carpet_removal,hardwood_floor_removal,drywall_removal,appliance_removal,heavy_item_removal,standing_water,mold_remediation,pump_needed,work_requested,notes,nonvegitative_debris_removal,vegitative_debris_removal,debris_blocking,house_roof_damage,outbuilding_roof_damage,tarps_needed,help_install_tarp,num_trees_down,num_wide_trees,trees_blocking,habitable,electricity,electrical_lines,unsafe_roof,other_hazards,claim_for_org,status,assigned_to,total_volunteers,hours_worked_per_volunteer,initials_of_resident_present,status_notes,prepared_by = row
            claiming_org = None
            reporing_org = None

            if name == None or name == "":
              name = "Unknown"

            if phone1 == None or phone1 == "":
              phone1 = "000-000-0000"

            NECHAMA = site_db.Site.get_by_id(3419001)
            TEXAS = site_db.Site.get_by_id(5664902681198592)
            if "NECHAMA" in claimed_by:
              claiming_org = NECHAMA

            if "Texas" in claimed_by:
              claiming_org = TEXAS

            if "NECHAMA" in reported_by:
              reporing_org = NECHAMA

            if "Texas" in reported_by:
              reporing_org = TEXAS

            logging.info(latitude)
            if address:
              q = db.Query(event_db.Event)
              q.filter("name =", "Texas-Oklahoma Floods")
              event = q.get()
              q = db.Query(site_db.Site)
              q.filter("event =", event.key())
              q.filter("name =", name)
              q.filter("latitude =", float(latitude))
              q.filter("longitude =", float(longitude))
              site = q.get()
              claiming_org = None
              reporting_org = None
              try:
                if len(claim_for_org) > 0:
                  claiming_org = site_db.Site.get_by_id(int(claimed_by))
                if len(reported_by) > 0:
                  reporting_org = site_db.Site.get_by_id(int(reported_by))
              except:
                pass


              try:
                if site:
                  site.name = name
                  site.claimed_by = claiming_org
                  site.reported_by = reporing_org
                  site.modified_by = None
                  site.prepared_by = prepared_by
                  site.request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
                  site.case_number = case_number
                  site.do_not_work_before = do_not_work_before
                  site.address = address
                  site.city = city
                  site.county = county
                  site.state = state
                  site.zip_code = zip_code
                  site.latitude = float(latitude)
                  site.longitude = float(longitude)
                  site.blurred_latitude = float(blurred_latitude)
                  site.blurred_longitude = float(blurred_longitude)
                  site.cross_street = cross_street
                  site.phone1 = phone1
                  site.phone2 = phone2
                  site.time_to_call = time_to_call
                  site.work_type = work_type
                  site.rent_or_own = rent_or_own
                  site.work_without_resident = work_without_resident
                  site.member_of_assessing_organization = member_of_assessing_organization
                  site.first_responder = first_responder
                  site.older_than_60 = older_than_60
                  site.special_needs = special_needs
                  site.severity = severity
                  site.damage_notes = damage_notes
                  site.flood_height = flood_height
                  site.floors_affected = floors_affected
                  site.carpet_removal = carpet_removal
                  site.hardwood_floor_removal = hardwood_floor_removal
                  site.drywall_removal = drywall_removal
                  site.appliance_removal = appliance_removal
                  site.heavy_item_removal = heavy_item_removal
                  site.standing_water = standing_water
                  site.mold_remediation = mold_remediation
                  site.pump_needed = pump_needed
                  site.work_requested = work_requested
                  site.notes = notes
                  site.nonvegitative_debris_removal = nonvegitative_debris_removal
                  site.vegitative_debris_removal = vegitative_debris_removal
                  site.debris_blocking = debris_blocking
                  site.house_roof_damage = house_roof_damage
                  site.outbuilding_roof_damage = outbuilding_roof_damage
                  site.tarps_needed = tarps_needed
                  site.help_install_tarp = help_install_tarp
                  site.num_trees_down = num_trees_down
                  site.num_wide_trees = num_wide_trees
                  site.trees_blocking = trees_blocking
                  site.habitable = habitable
                  site.electricity = electricity
                  site.electrical_lines = electrical_lines
                  site.unsafe_roof = unsafe_roof
                  site.other_hazards = other_hazards
                  site.claim_for_org = claim_for_org
                  site.status = status
                  site.assigned_to = assigned_to
                  site.total_volunteers = total_volunteers
                  site.hours_worked_per_volunteer = hours_worked_per_volunteer
                  site.initials_of_resident_present = initials_of_resident_present
                  site.status_notes = status_notes

                else:
                  # find site

                  site = site_db.Site(name=name,
                                      claimed_by = claiming_org,
                                      reported_by = reporing_org,
                                      modified_by = None,
                                      prepared_by = prepared_by,
                                      request_date= datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S'),
                                      case_number = case_number,
                                      do_not_work_before = do_not_work_before,
                                      address = address,
                                      city = city,
                                      county = county,
                                      state = state,
                                      zip_code = zip_code,
                                      latitude = float(latitude),
                                      longitude = float(longitude),
                                      blurred_latitude = float(blurred_latitude),
                                      blurred_longitude = float(blurred_longitude),
                                      cross_street = cross_street,
                                      phone1 = phone1,
                                      phone2 = phone2,
                                      time_to_call = time_to_call,
                                      work_type = work_type,
                                      rent_or_own = rent_or_own,
                                      work_without_resident = work_without_resident,
                                      member_of_assessing_organization = member_of_assessing_organization,
                                      first_responder = first_responder,
                                      older_than_60 = older_than_60,
                                      special_needs = special_needs,
                                      severity = severity,
                                      damage_notes = damage_notes,
                                      flood_height = flood_height,
                                      floors_affected = floors_affected,
                                      carpet_removal = carpet_removal,
                                      hardwood_floor_removal = hardwood_floor_removal,
                                      drywall_removal = drywall_removal,
                                      appliance_removal = appliance_removal,
                                      heavy_item_removal = heavy_item_removal,
                                      standing_water = standing_water,
                                      mold_remediation = mold_remediation,
                                      pump_needed = pump_needed,
                                      work_requested = work_requested,
                                      notes = notes,
                                      nonvegitative_debris_removal = nonvegitative_debris_removal,
                                      vegitative_debris_removal = vegitative_debris_removal,
                                      debris_blocking = debris_blocking,
                                      house_roof_damage = house_roof_damage,
                                      outbuilding_roof_damage = outbuilding_roof_damage,
                                      tarps_needed = tarps_needed,
                                      help_install_tarp = help_install_tarp,
                                      num_trees_down = num_trees_down,
                                      num_wide_trees = num_wide_trees,
                                      trees_blocking = trees_blocking,
                                      habitable = habitable,
                                      electricity = electricity,
                                      electrical_lines = electrical_lines,
                                      unsafe_roof = unsafe_roof,
                                      other_hazards = other_hazards,
                                      claim_for_org = claim_for_org,
                                      status = status,
                                      assigned_to = assigned_to,
                                      total_volunteers = total_volunteers,
                                      hours_worked_per_volunteer = hours_worked_per_volunteer,
                                      initials_of_resident_present = initials_of_resident_present,
                                      status_notes = status_notes
                                      )
                  #check_requred_fields(site)
                  #check_references(site)
                  #check_line_breaks(site)
                  #check_unicode(site)
                  #check_and_handle_duplicates(site, policy)
                  q = db.Query(event_db.Event)
                  q.filter("name =", "Texas-Oklahoma Floods")
                  event = q.get()
                  event_db.AddSiteToEvent(site, event.key().id())
              except Exception, err:
                errors[count] = err
    raise Exception(errors)
class BlobIterator:
    """Because the python csv module doesn't like strange newline chars and
    the google blob reader cannot be told to open in universal mode, then
    we need to read blocks of the blob and 'fix' the newlines as we go"""

    def __init__(self, blob_reader):
        self.blob_reader = blob_reader
        self.last_line = ""
        self.line_num = 0
        self.lines = []
        self.buffer = None

    def __iter__(self):
        return self

    def next(self):
        if not self.buffer or len(self.lines) == self.line_num + 1:
            self.buffer = self.blob_reader.read(1048576)  # 1MB buffer
            self.lines = self.buffer.splitlines()
            self.line_num = 0

            # Handle special case where our block just happens to end on a new line
            if self.buffer[-1:] == "\n" or self.buffer[-1:] == "\r":
                self.lines.append("")

        if not self.buffer:
            raise StopIteration

        if self.line_num == 0 and len(self.last_line) > 0:
            result = self.last_line + self.lines[self.line_num] + "\n"
        else:
            result = self.lines[self.line_num] + "\n"

        self.last_line = self.lines[self.line_num + 1]
        self.line_num += 1

        return result
