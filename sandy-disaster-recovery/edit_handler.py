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
import jinja2
import logging
import os
from google.appengine.ext import db
import json
import wtforms.validators
from datetime import datetime


# Local libraries.
import base
import site_db
import site_util
import form_db
import audit_db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('form.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')
menubox_template = jinja_environment.get_template('_menubox.html')
HATTIESBURG_SHORT_NAME = "derechos"
GEORGIA_SHORT_NAME = "gordon-barto-tornado"

class EditHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):
    if org.permissions == "Situational Awareness":
	self.redirect("/sit_aware_redirect")
	return
    #single_site_template = jinja_environment.get_template('single_site.html')
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')

    # lookup by id or case_number
    id = self.request.get('id', None)
    site_id = id
    mode_js = self.request.get("mode") == "js"
    case_number = self.request.get('case', None)
    if not id and case_number:
        q = db.GqlQuery("SELECT * FROM Site WHERE case_number=:1", case_number)
        if q.count() == 1:
            id = q[0].key().id()

    # if no id, 404
    if id is None:
      self.response.set_status(404)
      return

    # load site
    site = site_db.GetAndCache(int(id))
    if not site:
      self.response.set_status(404)
      return

    if not site.event.key() == event.key():
        self.redirect("/sites?message=The site you are trying to edit doesn't belong to the event you are signed in to. If you think you are seeing this message in error, contact your administrator")
        return
    #form = site_db.SiteForm(self.request.POST, site)
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #form = site_db.DerechosSiteForm(self.request.POST, site)
    post_json2 = site_db.SiteToDict(site)
    date_string = str(post_json2['request_date'])
    post_json2['request_date'] = date_string
    post_json2['event'] = site.event.name
    #post_json = {
      #"city": str(site.city),
      #"name": str(site.name),
      #"reported_by": str(site.reported_by.name),
    #}
    post_json = json.dumps(post_json2)
    #raise Exception(post_json)


    q = db.Query(form_db.IncidentForm)
    q.filter("incident =", event.key())
    query = q.get()

    # set it as form_stub
    # send to single site

    inc_form = None
    form=None
    if query:
      inc_form = query.form_html
    new_inc_form = inc_form.replace("checked ", "")
    if mode_js:
      new_inc_form = new_inc_form.replace('<input type="checkbox" id="ignore_similar" name="ignore_similar">', "")
      new_inc_form = new_inc_form.replace('Ignore similar matches', '')
      new_inc_form = new_inc_form.replace('Skip check for duplicates', '')
      new_inc_form = new_inc_form.replace('<input type=submit value="Submit request">', '')

      #raise Exception(post_json2)

      for k, v in post_json2.iteritems():
	if k in ["address", "appliances_claimed_by", "assigned_to", "city", "county", "cross_street", "do_not_work_before", "doors_claimed_by", "electrical_claimed_by", "email", "fema_housing_award", "flood_height", "floors_claimed_by", "hours_worked_per_volunteer", "hvac_claimed_by", "initials_of_resident_present", "kitchen_bath_claimed_by", "latitude", "longitude", "name", "phone1", "phone2", "plumbing_claimed_by", "prepared_by", "request_date", "roof_gutters_claimed_by", "secondary_contact_name", "secondary_contact_phone", "siding_claimed_by", "state", "tarps_needed", "time_to_call", "total_volunteers", "walls_claimed_by", "walls_flood_height", "windows_claimed_by", "zip_code"]:
	  try:
	    id_index = new_inc_form.index('id="' + k)
	    value_index = new_inc_form[id_index:].index("value")
	    if k in ["latitude", "longitude"] and event.short_name != "moore":
	      new_inc_form = new_inc_form[:id_index + value_index+7] + str(v) + new_inc_form[id_index + value_index+10:]
	    else:
	      new_inc_form = new_inc_form[:id_index + value_index+7] + str(v) + new_inc_form[id_index + value_index+7:]
	  except:
	    pass
        elif k=="num_trees_down" and v=="0" and event.short_name=="tx_ok_floods":
          pass
	elif k in ["appliances_damage_description", "appliances_notes", "damage_notes", "debris_description", "doors_damage_description", "doors_notes", "electrical_damage_description", "electrical_notes", "floors_damage_description", "floors_notes", "hvac_damage_description", "hvac_notes", "kitchen_bath_damage_description", "kitchen_bath_notes", "maintenance_appliances", "notes", "other_hazards", "other_needs", "plumbing_damage_description", "plumbing_notes", "roof_gutters_damage_description", "roof_gutters_notes", "siding_damage_description", "siding_notes", "special_needs", "status_notes", "walls_damage_description", "walls_notes", "windows_damage_description", "windows_notes", "work_requested"]:
	  try:
	    id_index = new_inc_form.index('id="' + k)
	    value_index = new_inc_form[id_index:].index(">")
	    new_inc_form = new_inc_form[:id_index + value_index+1] + str(v) + new_inc_form[id_index + value_index+1:]
	  except:
	    pass

	elif k in ["appliance_removal", "appliances_inspected", "appliances_permits_acquired", "appliances_waiver_signed", "appliances_waste_removal_required", "carpet_removal", "children_in_home", "claim_for_org", "doors_inspected", "doors_permits_acquired", "doors_waiver_signed", "doors_waste_removal_required", "drywall_removal", "dump_trailer_needed", "electrical_inspected", "electrical_lines", "electrical_permits_acquired", "electrical_waiver_signed", "electrical_waste_removal_required", "electricity", "first_responder", "floors_carpet", "floors_hardwood_floor", "floors_inspected", "floors_permits_acquired", "floors_subfloor", "floors_waiver_signed", "floors_waste_removal_required", "gutting_done", "habitable", "hardwood_floor_removal", "heavy_item_removal", "help_install_tarp", "hoarder", "house_roof_damage", "hvac_inspected", "hvac_permits_acquired", "hvac_waiver_signed", "hvac_waste_removal_required", "insured", "kitchen_bath_inspected", "kitchen_bath_permits_acquired", "kitchen_bath_waiver_signed", "kitchen_bath_waste_removal_required", "known_asbestos", "known_lead_paint", "maintenance_caulking", "maintenance_doors", "maintenance_drainage", "maintenance_electrical", "maintenance_furnace", "maintenance_hvac", "maintenance_plumbing", "maintenance_roof", "maintenance_septic", "maintenance_sewer_septic", "maintenance_siding", "maintenance_water_heater", "maintenance_windows", "member_of_assessing_organization", "mold_drying", "mold_hvac", "mold_remediation", "mold_replace_studs", "mold_scraping", "mold_spraying", "mold_supression_done", "needs_visual", "nonvegitative_debris_removal", "older_than_60", "outbuilding_roof_damage", "plumbing_inspected", "plumbing_permits_acquired", "plumbing_septic", "plumbing_waiver_signed", "plumbing_waste_removal_required", "pump_needed", "release_can_sign", "release_form", "release_org_sign", "roof_gutters_inspected", "roof_gutters_permits_acquired", "roof_gutters_shingles", "roof_gutters_tarping", "roof_gutters_waiver_signed", "roof_gutters_waste_removal_required", "siding_inspected", "siding_permits_acquired", "siding_waiver_signed", "siding_waste_removal_required", "standing_water", "unsafe_roof", "vegitative_debris_removal", "walls_drywall", "walls_framing", "walls_gutting", "walls_inspected", "walls_insulation", "walls_mold_remediation", "walls_permits_acquired", "walls_waiver_signed", "walls_waste_removal_required", "windows_inspected", "windows_permits_acquired", "windows_waiver_signed", "windows_waste_removal_required", "work_without_resident"]:
	  try:
	    if v == "y":
	      id_index = new_inc_form.index('id="' + k)
	      value_index = new_inc_form[id_index:].index(">")
	      new_inc_form = new_inc_form[:id_index + value_index] + "checked" + new_inc_form[id_index + value_index:]
	  except:
	    pass

	elif k in ["severity", "fake_radio", "priority", "destruction_level"]:
	  #try:
	  if event.short_name == "columbia_tornado":
            pass
          else:
            logging.debug(event.short_name)
            logging.debug(k + " is the key")
            logging.debug(str(v) + " is the value")
            logging.debug(str(k) + " is the key")
            if event.short_name == "eastcoast_snow" and k == "priority":
              pass
            elif event.short_name == "hattiesburg" and k == "num_trees_down":
              pass
            elif event.short_name == "tx_ok_floods" and k == "priority":
              pass
            else:
              logging.info(k, v)
              try: 
                id_index = new_inc_form.index('name="' + k + '" type="radio" value="' + str(v))
              except:
                pass

	  #new_inc_form = new_inc_form[id_index-350:id_index+350].replace("checked ", "")

	  new_inc_form = new_inc_form[:id_index] + " checked " + new_inc_form[id_index:]
	elif k in ["appliances_floors_affected", "appliances_status", "debris_blocking", "doors_floors_affected", "doors_status", "dwelling_type", "electrical_floors_affected", "electrical_status", "floors_affected", "floors_floors_affected", "floors_status", "hvac_floors_affected", "hvac_status", "kitchen_bath_floors_affected", "kitchen_bath_status", "mold_amount", "num_trees_down", "num_wide_trees", "plumbing_floors_affected", "plumbing_status", "rent_or_own", "roof_gutters_floors_affected", "roof_gutters_status", "siding_floors_affected", "siding_status", "status", "trees_blocking", "walls_floors_affected", "walls_status", "windows_floors_affected", "windows_status", "work_type"]:
	  if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME] and k == "floors_affected":
	    pass
          elif event.short_name=="tx_ok_floods" and k=="num_trees_down" and v=="0":
            pass
	  else:
	    logging.debug(event.short_name)
	    logging.debug(k + " is the key")
            logging.debug(v + " is the value")
	    id_index = new_inc_form.index('id="' + k)
	    try:
              value_index = new_inc_form[id_index:].index('value="' + str(v))
              length = 0
              if v != None:
                length = len(str(v))

              new_inc_form = new_inc_form[:id_index + value_index+8 + length] + "selected" + new_inc_form[id_index + value_index+8 + length:]
            except ValueError, err:
              logging.error(err)




	#raise Exception(new_inc_form[:id_index + 380])
	#except:
	  #pass      # find 'id=" + k
      # find type=", (index)
      # find ", (index)
      # What's in between is the type.
      # If the type == Checkbox, and value == y
      # find >, (index)
      # add "checked" just before
    single_site = single_site_template.render(
        { "form": form,
          "org": org,
	  "incident_form_block": new_inc_form,
	  "post_json": post_json,
          })

    #raise Exception(query.form_html)
    self.response.out.write(template.render(
          {"mode_js": self.request.get("mode") == "js",
           "menubox" : menubox_template.render({"org": org, "event": event}),
           "single_site": single_site,
           "event_name": event.name,
           "site_id": site_id,
           "form": form,
           "id": id,
	   "post_json": post_json	,
           "page": "/edit"}))

  def AuthenticatedPost(self, org, event):
    if org.permissions == "Situational Awareness":
      self.redirect("/sit_aware_redirect")
      return
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
      #single_site_template = jinja_environment.get_template('single_site_derechos.html')
    try:
      id = int(self.request.get('_id'))
    except:
      return
    site = site_db.Site.get_by_id(id)
    try:
      audit_db.create(site, "edit", org)
    except:
      logging.error("Audit exception")
    old_status = site.status
    data = site_db.StandardSiteForm(self.request.POST, site)
    new_status = data.status.data
    if old_status != new_status:
      if not site.claimed_by: 
        site.claimed_by = org
        site.claim_for_org = "y"
    # raise Exception(old_status, new_status.data)
    #if event.short_name in [HATTIESBURG_SHORT_NAME, GEORGIA_SHORT_NAME]:
        #form = site_db.DerechosSiteForm(self.request.POST, site)

    # un-escaping data caused by base.py = self.request.POST[i] = cgi.escape(self.request.POST[i])
    data.name.data = site_util.unescape(data.name.data)


    data.priority.data = int(data.priority.data)
    data.name.validators = data.name.validators + [wtforms.validators.Length(min = 1, max = 100,
                             message = "Name must be between 1 and 100 characters")]
    data.phone1.validators = data.phone1.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a primary phone number")]
    data.city.validators = data.city.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a city name")]
    data.state.validators = data.state.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please enter a state name")]
    data.work_type.validators = data.work_type.validators + [wtforms.validators.Length(
        min = 1, max = 100,
        message = "Please set a primary work type")]


    case_number = site.case_number
    claim_for_org = self.request.get("claim_for_org") == "y"

    mode_js = self.request.get("mode") == "js"
    if data.validate():
      #setattr(site, "longitude", lng_float)
      #setattr(site, "latitude", lat_float)
      # Save the data, and redirect to the view page
      for f in data:
        # In order to avoid overriding fields that didn't appear
        # in this form, we have to only set those that were explicitly
        # set in the post request.
        in_post = self.request.get(f.name, default_value = None)
        if in_post is None:
          continue
        setattr(site, f.name, f.data)
      if claim_for_org == "y":
        site.claimed_by = org
      # clear assigned_to if status is unassigned
      if data.status.data == 'Open, unassigned':
        site.assigned_to = ''


      for k, v in self.request.POST.iteritems():
	if k not in site_db.STANDARD_SITE_PROPERTIES_LIST:

	  if k == "request_date":
	    try:
	      date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
	      setattr(site, k, date_object)
	    except:
	      date_object = datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
	      setattr(site, k, date_object)
	  else:
            setattr(site, k, v)
      site_db.PutAndCache(site)

      if mode_js:
        # returning a 200 is sufficient here.
        return
      else:
        self.redirect('/map?id=%d' % id)
    else:
      q = db.Query(form_db.IncidentForm)
      q.filter("incident =", event.key())
      query = q.get()

      # set it as form_stub
      # send to single site

      inc_form = None
      form=None
      if query:
	inc_form = query.form_html

      post_json2 = site_db.SiteToDict(site)
      date_string = str(post_json2['request_date'])
      post_json2['request_date'] = date_string
      post_json2['event'] = site.event.name
      #post_json = {
	#"city": str(site.city),
	#"name": str(site.name),
	#"reported_by": str(site.reported_by.name),
      #}
      post_json = json.dumps(post_json2)

      single_site = single_site_template.render(
          { "form": data,
            "org": org,
	    "incident_form_block": inc_form,
	  })
      if mode_js:
        self.response.set_status(400)
      self.response.out.write(template.render(
          {"mode_js": mode_js,
           "menubox" : menubox_template.render({"org": org, "event": event}),
           "errors": data.errors,
           "form": data,
           "single_site": single_site,
           "id": id,
	   "post_json": post_json,
           "page": "/edit"}))
