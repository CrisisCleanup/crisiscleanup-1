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
      left_count = 0
      deleted_count =0
      string = "Y119,Y120,Y121,Y122,Y123,Y124,Y125,Y126,Y127,Y128,Y129,Y130,Y131,Y132,Y133,Y134,Y135,Y136,Y137,Y138,Y139,Y140,Y144,Y145,Y146,Y147,Y148,Y149,Y150,Y151,Y152,Y153,Y154,Y155,Y156,Y157,Y158,Y159,Y161,Y162,Y163,Y164,Y165,Y166,Y167,Y168,Y169,Y170,Y171,Y172,Y173,Y174,Y175,Y176,Y177,Y178,Y179,Y180,Y181,Y182,Y183,Y184,Y185,Y186,Y187,Y188,Y189,Y190,Y191,Y192,Y193,Y194,Y195,Y196,Y197,Y198,Y199,Y200,Y201,Y202,Y203,Y204,Y205,Y206,Y207,Y208,Y209,Y210,Y211,Y212,Y213,Y214,Y215,Y216,Y217,Y218,Y219,Y220,Y221,Y222,Y223,Y224,Y225,Y226,Y227,Y228,Y229,Y230,Y231,Y232,Y233,Y234,Y235,Y236,Y237,Y238,Y239,Y240,Y241,Y242,Y243,Y244,Y245,Y246,Y247,Y248,Y249,Y250,Y251,Y252,Y253,Y254,Y255,Y256,Y257,Y258,Y259,Y260,Y261,Y262,Y263,Y264,Y265,Y266,Y267,Y268,Y269,Y270,Y271,Y272,Y273,Y274,Y275,Y276,Y277,Y278,Y279,Y280,Y281,Y282,Y283,Y284,Y285,Y286,Y287,Y288,Y289,Y290,Y291,Y292,Y293,Y294,Y295,Y296,Y297,Y298,Y299,Y300,Y301,Y302,Y303,Y304,Y305,Y306,Y307,Y308,Y309,Y310,Y311,Y312,Y313,Y314,Y315,Y316,Y317,Y318,Y319,Y320,Y321,Y322,Y323,Y324,Y325,Y326,Y327,Y328,Y329,Y330,Y331,Y332,Y333,Y334,Y335,Y336,Y337,Y338,Y339,Y340,Y341,Y342,Y343,Y344,Y345,Y346,Y347,Y348,Y349,Y350,Y351,Y352,Y353,Y358,Y359,Y360,Y361,Y362,Y363,Y364,Y365,Y366,Y367,Y368,Y369,Y370,Y371,Y372,Y373,Y374,Y375,Y376,Y377,Y378,Y379,Y380,Y381,Y382,Y383,Y384,Y385,Y386,Y387,Y388,Y389,Y390,Y391,Y392,Y393,Y394,Y395,Y396,Y397,Y0,Y1,Y10,Y100,Y101,Y102,Y103,Y104,Y105,Y106,Y107,Y108,Y109,Y11,Y110,Y111,Y112,Y113,Y114,Y115,Y116,Y117,Y118,Y12,Y13,Y14,Y141,Y142,Y143,Y15,Y16,Y160,Y17,Y18,Y19,Y2,Y20,Y21,Y22,Y23,Y24,Y25,Y26,Y27,Y28,Y29,Y3,Y30,Y31,Y32,Y33,Y34,Y35,Y36,Y37,Y38,Y39,Y4,Y40,Y41,Y42,Y43,Y44,Y45,Y46,Y47,Y48,Y49,Y5,Y50,Y51,Y52,Y53,Y54,Y55,Y56,Y57,Y58,Y59,Y6,Y60,Y61,Y62,Y63,Y64,Y65,Y66,Y67,Y68,Y69,Y7,Y70,Y71,Y72,Y73,Y74,Y75,Y76,Y77,Y78,Y79,Y8,Y80,Y81,Y82,Y83,Y84,Y85,Y86,Y87,Y88,Y89,Y9,Y90,Y91,Y92,Y93,Y94,Y95,Y96,Y97,Y98,Y99"
      arr = string.split(",")
      for case_number in arr:
        q = db.Query(audit_db.Audit)
        q.filter("case_number =", case_number)
        audit_object = q.get()  
        if audit_object:
          audit_object.delete()
      for case_number in arr:
        q = db.Query(audit_db.Audit)
        q.filter("case_number =", case_number)
        audit_object = q.get()
        if audit_object:
          left_count +=1
        else:
          deleted_count += 1
      logging.info("left_count" + str(left_count))
      logging.info("deleted_count" + str(deleted_count))



        # event_short_name = self.request.get("event")
        # duplicate_detection = self.request.get("duplicate")
        # duplicate_method = self.request.get("duplicate_method_select")
        # upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        # blob_info = upload_files[0]
        # blob_reader = blobstore.BlobReader(blob_info.key())
        # blob_iterator = BlobIterator(blob_reader)
        # reader = csv.reader(blob_iterator, 'rb')
        # for row in reader:
        #   raise Exception(row)

        # q = db.Query(event_db.Event)
        # q.filter("short_name =", event_short_name)
        # event_object = q.get()
        # num_sites_start = event_object.num_sites
        # errors, count, duplicates, saved_duplicates, saved_new, has_references_count = process_csv(blob_info, event_object, duplicate_detection, duplicate_method)
        # blobstore.delete(blob_info.key())  # optional: delete file after import
        # #self.redirect("/")

        # template_params = {
        #   "errors": errors,
        #   "count": count,
        #   "error_count": len(errors),
        #   "event_name": event_object.name,
        #   "duplicates": duplicates,
        #   "saved_duplicates": saved_duplicates,
        #   "saved_new": saved_new,
        #   "has_references_count": has_references_count
        # }
        # self.response.out.write(template.render(template_params))



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
