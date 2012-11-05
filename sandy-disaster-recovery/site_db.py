from wtforms.ext.appengine.db import model_form
from google.appengine.ext import db

class Site(db.Model):
  # Data about the site itself.
  name = db.StringProperty(required = True)
  request_date = db.DateTimeProperty(auto_now_add=True)
  address = db.StringProperty(required = True)
  city = db.StringProperty()
  state = db.StringProperty()
  zip_code = db.StringProperty()
  cross_street = db.StringProperty()
  landmark = db.StringProperty()
  phone1 = db.StringProperty()
  phone2 = db.StringProperty()
  time_to_call = db.StringProperty()
  property_type = db.StringProperty(
      choices=set(["Home", "Town House", "Multi-Unit", "Business"]))
  renting = db.BooleanProperty()
  work_without_resident = db.BooleanProperty()
  ages_of_residents = db.StringProperty()
  special_needs = db.StringProperty(multiline=True)
  electricity = db.BooleanProperty()
  standing_water = db.BooleanProperty()
  tree_damage = db.BooleanProperty()
  tree_damage_details = db.StringProperty(multiline=True)
  habitable = db.BooleanProperty()
  work_requested = db.StringProperty(multiline=True)
  others_help = db.StringProperty(multiline=True)
  debris_removal_only = db.BooleanProperty()
  work_type = db.StringProperty(choices=set(["Flood", "Trees", "Other"]))
  tree_diameter = db.StringProperty()
  electrical_lines = db.BooleanProperty()
  cable_lines = db.BooleanProperty()
  cutting_cause_harm = db.BooleanProperty()
  other_hazards = db.StringProperty(multiline = True)
  insurance = db.StringProperty(multiline = True)
  notes = db.StringProperty(multiline = True)
  latitude = db.FloatProperty()
  longitude = db.FloatProperty()
  # Priority assigned by organization (1 is highest).
  priority = db.IntegerProperty()
  # Name of org. rep (e.g. "Jill Smith")
  inspected_by = db.StringProperty()

  # Metadata
  # TODO(Bruce): We need to add an "assigned organization" field, once we have
  # organizations.
  status = db.StringProperty(
      choices=set(["Open, unassigned", "Closed, out of scope"]))
  date_closed = db.DateTimeProperty()
  # Number of volunteers who helped.
  total_volunteers = db.FloatProperty()
  # Number of hours that each volunteer worked.
  # There's apparently an assumption that all volunteers worked the same amount
  # of time, since total time for the project is calculated as
  # total_volunteers * hours_worked_per_volunteer.
  hours_worked_per_volunteer = db.FloatProperty()


SiteForm = model_form(Site)
