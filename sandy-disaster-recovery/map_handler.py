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
import datetime
import jinja2
import json
import os
from google.appengine.ext import db
from google.appengine.api import memcache
import json

# Local libraries.
import base
import event_db
import key
import site_db
import page_db
from models import incident_definition
from helpers import populate_incident_form


dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja_environment.get_template('map.html')
menubox_template = jinja_environment.get_template('_menubox_bootstrap.html')
single_site_template = jinja_environment.get_template('single_site_incident_form.html')



class MapHandler(base.AuthenticatedHandler):
  def AuthenticatedGet(self, org, event):

    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    #if inc_def_query:
      ##raise Exception(id)
      #phases_links = populate_phase_links(json.loads(inc_def_query.phases_json), id)

    #phase_id = None
    
    phase_number = 0
    hidden_elements = {
      "site_id": id,
      "phase_number": phase_number
    }
    defaults_json = None

    string = "<h2>No Form Added Yet</h2><p>To add a form for this incident, contact your administrator.</p>"
    label = ""
    paragraph = ""
    phases_links = ""
    submit_button = ""
    if inc_def_query:
      string, label, paragraph= populate_incident_form.populate_incident_form(json.loads(inc_def_query.forms_json), phase_number, defaults_json)
      
    single_site = single_site_template.render(
    { "form": 1,
      "org": 2,
      "incident_form_block": string,
      "post_json": 4,
    })
    
    phase_number = self.request.get("phase_number")
    if not phase_number:
      phase_number = 0
    q = db.Query(incident_definition.IncidentDefinition)
    q.filter("incident =", event.key())
    inc_def_query = q.get()
    
    phases_json = json.loads(inc_def_query.phases_json)
    phase_id = phases_json[int(phase_number)]['phase_id']
      
    filters = [
              #["debris_only", "Remove Debris Only"],
              #["electricity", "Has Electricity"],
              #["no_standing_water", "No Standing Water"],
              #["not_habitable", "Home is not habitable"],
              ["Flood", "Primary problem is flood damage"],
              ["Trees", "Primary problem is trees"],
              ["Goods or Services", "Primary need is goods and services"]]
              #["CT", "Connecticut"],
              #["NJ", "New Jersey"],
              #["NY", "New York"]]

    if org:
      filters = [["claimed", "Claimed by " + org.name],
                 ["unclaimed", "Unclaimed"],
                 ["open", "Open"],
                 ["closed", "Closed"],
                 ["reported", "Reported by " + org.name],
                 ] + filters

      site_id = self.request.get("id")
      # default to 15
      zoom_level = self.request.get("z", default_value = "15")

      template_values = page_db.get_page_block_dict()
      template_values.update({
          "version" : os.environ['CURRENT_VERSION_ID'],
          "shortname": event.short_name,
          "organization_map_latitude": inc_def_query.organization_map_latitude,
          "organization_map_longitude": inc_def_query.organization_map_longitude,
          "organization_map_zoom": inc_def_query.organization_map_zoom,
          "organization_map_cluster": inc_def_query.organization_map_cluster,
          "kml_layer": inc_def_query.organization_map_url,
          "organization_map_title": inc_def_query.organization_map_title,
          #"uncompiled" : True,
          "counties" : event.counties,
          "org" : org,
          "menubox" : menubox_template.render({"org": org,
                                             "event": event,
                                             "include_search": True,
                                             "admin": org.is_admin,
                                             "phase_links": populate_phase_links(event, phase_number)
                                             }),
          "status_choices" : [json.dumps(c) for c in
                              site_db.Site.status.choices],
          "filters" : filters,
          "demo" : False,
          "zoom_level" : zoom_level,
          "site_id" :  site_id,
	  "event_name": event.name,
	  "edit_form": 1,
	  "single_site": None

        })
    else:
      # TODO(Jeremy): Temporary code until this handler scales.
      self.redirect("/authentication?destination=/map")
      return
      # Allow people to bookmark an unauthenticated event map,
      # by setting the event ID.
      event = event_db.GetEventFromParam(self.request.get("event_id"))
      if not event:
        self.response.set_status(404)
        return
      template_values = page_db.get_page_block_dict()
      template_values.update({
          "sites" :
             [json.dumps({
                 "latitude": round(s.latitude, 2),
                 "longitude": round(s.longitude, 2),
                 "debris_removal_only": s.debris_removal_only,
                 "electricity": s.electricity,
                 "standing_water": s.standing_water,
                 "tree_damage": s.tree_damage,
                 "habitable": s.habitable,
                 "electrical_lines": s.electrical_lines,
                 "cable_lines": s.cable_lines,
                 "cutting_cause_harm": s.cutting_cause_harm,
                 "work_type": s.work_type,
                 "state": s.state,
                 }) for s in [p[0] for p in site_db.GetAllCached(event)]],
          "filters" : filters,
          "demo" : True,
          "shortname": event.short_name,
          "single_site": None
        })
    self.response.out.write(template.render(template_values))



def populate_phase_links(event, this_phase = None):
  if this_phase == None:
    this_phase = "0"
  q = db.Query(incident_definition.IncidentDefinition)
  q.filter("incident =", event.key())
  inc_def_query = q.get()
  if inc_def_query == None:
    return ""
  
  phases_json = json.loads(inc_def_query.phases_json)
  
  links = "<br><br><b>Phases:</b><br>"
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    separator = ""
    if i > 0:
      separator = " | "
    #raise Exception(str(i) + this_phase)

    if str(i) == str(this_phase):

      links = links + separator + '<a style="font-weight:bold; font-size:150%" href="/map?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    else:
      links = links + separator + '<a href="/map?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    i+=1
    
  return links