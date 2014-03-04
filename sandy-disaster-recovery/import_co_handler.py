import jinja2
import os
import base
import site_db
import csv
import geopy
import logging
from geopy import geocoders  
import metaphone
jinja_environment = jinja2.Environment(
loader=jinja2.FileSystemLoader('templates/html/default/'))
template = jinja_environment.get_template('import.html')
from google.appengine.ext import db

headers_list = ['name', 'request_date', 'address', 'city', 'county', 'state', 'cross_street', 'phone1', 'phone2', 'time_to_call', 'work_type', 'rent_or_own', 'work_without_resident', 'member_of_assessing_organization', 'first_responder', 'older_than_60', 'special_needs', 'priority', 'flood_height', 'floors_affected', 'carpet_removal', 'hardwood_floor_removal', 'drywall_removal', 'appliance_removal', 'heavy_item_removal', 'standing_water', 'mold_remediation', 'pump_needed', 'work_requested', 'notes', 'nonvegitative_debris_removal', 'vegitative_debris_removal', 'house_roof_damage', 'outbuilding_roof_damage', 'tarps_needed', 'help_install_tarp', 'num_trees_down', 'num_wide_trees', 'habitable', 'electricity', 'electrical_lines', 'unsafe_roof', 'other_hazards', 'claim_for_org', 'status', 'assigned_to', 'total_volunteers', 'hours_worked_per_volunteer', 'initials_of_resident_present', 'status_notes', 'prepared_by', 'do_not_work_before']
class ImportCOHandler(base.RequestHandler):
    def get(self):	
      self.response.out.write(template.render(
        {
            "message": self.request.get("message"),
	    "logged_in": True,
        }))   
    def post(self):
	failures_array = []
	to_put = []

        csv_file = self.request.get('file')
        cr = csv.DictReader(csv_file.split('\n'))
        csv_headers = cr.fieldnames
        if set(csv_headers) != set(headers_list):
	  self.response.write("CSV headers to not match CO Flood Headers")
	  return
	g = geocoders.GoogleV3()

	#### Validate csv has correct headers
	complete = False
	for row in cr:

	    p  = site_db.Site(name=row["name"], address=row["address"])
	    lat = None
	    lng = None
	    address_string = row["address"] + " " + row["city"] + " " + row["state"]
	    #try:
	    if len(address_string) > 10:
	      try:
		place, (lat, lng) = g.geocode(address_string.lower())
		logging.debug(lat)
		logging.debug(lng)
		logging.debug(place)

	      except geopy.geocoders.googlev3.GTooManyQueriesError:
		failures_array.append(address_string)
		continue
		#geocodes = g.geocode(address_string.lower())
		#raise Exception(geocodes[0])
	    
	    setattr(p, "latitude", float(lat))
	    setattr(p, "longitude", float(lng))
	    for key in row.keys():
		initial_value = str(row[key])
		#new_value = quoted_value = urllib.quote(initial_value.encode('utf-8'))
		new_value = unicode(initial_value, 'utf-8')

		setattr(p, key, new_value)
		#if key == "name":
		  #name_metaphone = metaphone.dm(unicode(row[key]))
		  #setattr(p, "name_metaphone", str(name_metaphone[0]))
	    q = site_db.Site.all()
	    q.filter('latitude = ', float(lat))
	    q.filter('longitude = ', float(lng))
	    #q.filter('name_metaphone = ', str(name_metaphone[0]))

	    if not q.get():
	      to_put.append(p)
	    else:
	      pass
	    complete = True
	    #except:
	      #failures_array.append(address_string)
	      #continue
	    
	   
	if complete:
	  final_list = list(set(to_put))
	  db.put(final_list)
	for i in failures_array:
	  self.response.write(i)
	  self.response.write("<br/>")
