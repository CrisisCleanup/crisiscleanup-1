import csv
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
import site_db
import event_db
import organization
from datetime import datetime
import logging
import jinja2
import os
import urllib
from google.appengine.ext import db
import audit_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('upload_complete.html')

EVENT = None

fields = ["claimed_by", "reported_by", "modified_by", "case_number", "days", "name", "request_date", "address", "city", "county", "state", "zip_code", "latitude", "longitude", "latitude_blur", "longitude_blur", "cross_street", "phone1", "phone2", "work_type", "older_than_60", "special_needs", "roof_clearing", "dig_out_car", "ice_removal", "driveway_clearing", "walkway_clearing", "stair_clearing", "ramp_clearing", "deck_clearing", "leaking", "structural_problems", "roof_collapse", "needs_food", "needs_clothing", "needs_shelter", "needs_fuel", "needs_tarp", "tree_debris", "needs_visual", "other_needs", "notes", "other_hazards", "claim_for_org", "status", "assigned_to", "total_volunteers", "hours_worked_per_volunteer", "initials_of_resident_present", "status_notes", "prepared_by", "do_not_work_before"]

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        event_short_name = self.request.get("event")
        duplicate_detection = self.request.get("duplicate")
        duplicate_method = self.request.get("duplicate_method_select")
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        q = db.Query(event_db.Event)
        q.filter("short_name =", event_short_name)
        event_object = q.get()
        num_sites_start = event_object.num_sites
        errors, count, duplicates, saved_duplicates, saved_new, has_references_count = process_csv(blob_info, event_object, duplicate_detection, duplicate_method)
        blobstore.delete(blob_info.key())  # optional: delete file after import
        #self.redirect("/")

        template_params = {
          "errors": errors,
          "count": count,
          "error_count": len(errors),
          "event_name": event_object.name,
          "duplicates": duplicates,
          "saved_duplicates": saved_duplicates,
          "saved_new": saved_new,
          "has_references_count": has_references_count
        }
        self.response.out.write(template.render(template_params))



def process_csv(blob_info, event, duplicate_detection, duplicate_method):
    blob_reader = blobstore.BlobReader(blob_info.key())
    blob_iterator = BlobIterator(blob_reader)
    reader = csv.reader(blob_iterator)

    headers = reader.next()

    count = 0
    duplicates = 0
    saved_duplicates = 0
    saved_new = 0
    has_references_count = 0
    ignored=0
    errors = {}
    for row in reader:
        data = {}
        count += 1
        row_count = 0
        for value in row:
          data[headers[row_count]] = value
          row_count += 1

        try:
          if duplicate_detection:
            site = duplicate_detector(event, data, duplicate_detection)
            if site:
              duplicates += 1
              if duplicate_method == "all":
                success = edit_site(site, data)
                saved_duplicates += 1
              elif duplicate_method == "references":
                success = edit_references(site, data)
                saved_duplicates += 1
              elif duplicate_method == "ignore":
                ignored += 1
                pass
              elif duplicate_method == "references_work_type":
                success = edit_references_if_none_exists(site, data)
                saved_duplicates += 1
            else:
              success = add_site(data, event)
              saved_new += 1
          else:
            add_site(data, event)
            saved_new += 1
        except Exception, err:
          errors[count] = err
    return errors, count, duplicates, saved_duplicates, saved_new, has_references_count

def add_site(data, event):
  site = site_db.Site(name= data["name"],
  request_date= datetime.strptime(data["request_date"], '%Y-%m-%d %H:%M:%S'),
  address = data["address"],
  phone1 = data["phone1"],
  work_type = data["work_type"])
  for key in data:
    if key not in ["name", "request_date", "address", "phone1", "work_type"]:
      # special cases, claimed_by, reported_by, modified_by, prepared_by, latitude, latitude_blur, request_date
      if key in ["latitude", "longitude", "latitude_blur", "longitude_blur"]:
        setattr(site, key, float(data[key]))
      elif key == "request_date":
        setattr(site, key, datetime.strptime(data[key], '%Y-%m-%d %H:%M:%S'))
      elif key in ["reported_by", "claimed_by"]:
        d = str(data[key])
        if d:
          c = float(str(d))
          b = int(c)
          setattr(site, key, organization.Organization.get_by_id(b))
      elif key == "modified_by":
        setattr(site, key, None)
      else:
        setattr(site, key, data[key])
  success = event_db.AddSiteToEvent(site, event.key().id())
  add_audit(site, "create")
  return success

def edit_site(site, data):
  for key in data:
    # special cases, claimed_by, reported_by, modified_by, prepared_by, latitude, latitude_blur, request_date
    if key in ["latitude", "longitude", "latitude_blur", "longitude_blur"]:
      setattr(site, key, float(data[key]))
    elif key == "request_date":
      setattr(site, key, datetime.strptime(data[key], '%Y-%m-%d %H:%M:%S'))
    elif key in ["reported_by", "claimed_by"]:
      d = str(data[key])
      if d:
        c = float(str(d))
        b = int(c)
        setattr(site, key, organization.Organization.get_by_id(b))
    elif key == "modified_by":
      setattr(site, key, None)
    else:
      setattr(site, key, data[key])
  success = site.put()
  add_audit(site, "edit")
  return success

def edit_references(site, data, work_type=False):
  for key in data:
    if key in ["reported_by", "claimed_by"]:
      d = str(data[key])
      if d:
        c = float(str(d))
        b = int(c)
        setattr(site, key, organization.Organization.get_by_id(b))
    if work_type == True:
      if key == "work_type" and data[key] != "Report":
        setattr(site, key, data[key])
  success = site.put()
  add_audit(site, "edit")
  return success

def edit_references_if_none_exists(site, data):
  for key in data:
    if key in ["reported_by", "claimed_by"]:
      d = str(data[key])
      if d:
        if d == "5851736711364600":
          d = "5851736711364608"
        if d == "5321360863657980":
          d = "5321360863657984"
        if d == "5088174472691710":
          d = "5088174472691712"
        c = float(str(d))
        b = int(c)
        org = organization.Organization.get_by_id(b)
        logging.info(site.case_number)
        if site.case_number == "R1057":
          logging.info(site.name)
          logging.info(site.claimed_by)
          logging.info(site.reported_by)
          logging.info(org)
        setattr(site, key, organization.Organization.get_by_id(b))
  success = site.put()
  add_audit(site, "edit")
  return success

def duplicate_detector(event, data, duplicate_detection):
    # determine filters by duplicate_detection
    q = db.Query(site_db.Site)
    #raise Exception(data["latitude"], data["name"], data["longitude"])
    q.filter("event =", event.key())
    if "name" in duplicate_detection:
      q.filter("name =", data["name"])
    if "lat" in duplicate_detection:
      q.filter("latitude =", float(data["latitude"]))
    if "lng" in duplicate_detection:
      q.filter("longitude =", float(data["longitude"]))
    site = q.get()
    #raise Exception(site)
    return site

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

def add_audit(site, action):
  try:
    audit_db.create(action, site, site.reported_by)
  except:
    logging.error("Audit error")
