var clusterer=null;
var all_markers = [];
var open_filter_state = null;
var closed_filter_state = null;
var claimed_filter_state = null;
var unclaimed_filter_state = null;
var debris_filter_state = null;
$(function(){
  

    var myLatlng = new google.maps.LatLng(38.50, -85.35);
    var mapOptions = {
        zoom: 5,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
  var map = new google.maps.Map(document.getElementById("map-canvas"),
    mapOptions);
  google.maps.event.addDomListener(window, 'load', initialize);

  MarkerClusterer.IMAGE_PATH = "/icons/m";
  var markerCluster = new MarkerClusterer(map);
  clusterer = markerCluster;
  
  $("#filters_div").on( "click", "#open",  function() {
    if (open_filter_state == null || open_filter_state == false) {
      open_filter_state = true;
    } else {
      open_filter_state = false;
    }
    set_new_markers();
  });
  
  $("#filters_div").on( "click", "#closed",  function() {
    if (closed_filter_state == null || closed_filter_state == false) {
      closed_filter_state = true;
    } else {
      closed_filter_state = false;
    }
    set_new_markers();
  });
  
  $("#filters_div").on( "click", "#claimed",  function() {
    if (claimed_filter_state == null || claimed_filter_state == false) {
      claimed_filter_state = true;
    } else {
      claimed_filter_state = false;
    }
    set_new_markers();
  });
    
  $("#filters_div").on( "click", "#unclaimed",  function() {
    if (unclaimed_filter_state == null || unclaimed_filter_state == false) {
      unclaimed_filter_state = true;
    } else {
      unclaimed_filter_state = false;
    }
    set_new_markers();
  });
  
  $("#filters_div").on( "click", "#Debris",  function() {
    if (debris_filter_state == null || debris_filter_state == false) {
      debris_filter_state = true;
    } else {
      debris_filter_state = false;
    }
    set_new_markers();
  });
  // onclick
  // console.log all_markers
  // if it comes up, then just search, filter, and resend to clusterer.addMarkers

})

var set_new_markers = function() {
  var new_markers = [];

  if (open_filter_state != true && closed_filter_state != true && unclaimed_filter_state != true && claimed_filter_state != true && debris_filter_state != true)  {
    open_filter_state = true; 
  }
  // if all are false, set open to true
  if (open_filter_state == true && closed_filter_state == true) {
    clusterer.clearMarkers(); 
  } else {
    for (var i = 0; i < all_markers.length; i++) {
      if (open_filter_state == true) { 
	  if (all_markers[i]['site_info']['status'].indexOf("Open") != -1) {
	    // add  
	      new_markers.push(all_markers[i]);
	  }
      }
      
      if (closed_filter_state == true) { 
	  if (all_markers[i]['site_info']['status'].indexOf("Closed") != -1) {
	    // add  
	      new_markers.push(all_markers[i]);
	  }
      }

      if (claimed_filter_state == true) { 
	  if (all_markers[i]['site_info']['claimed_by'] != null) {
	    // add  
	      new_markers.push(all_markers[i]);
	  }
      }
      
      if (unclaimed_filter_state == true) { 
	  if (all_markers[i]['site_info']['claimed_by'] == null) {
	    // add  
	      new_markers.push(all_markers[i]);
	  }
      }
      
      if (debris_filter_state == true) {
	// must do this by open, closed, etc
	  if (all_markers[i]['site_info']['work_type'] == "Debris") {
	    new_markers.push(all_markers[i]);
	  }
      }
      
    }
    
    console.log("234");
    console.log(new_markers);
    clusterer.clearMarkers();
    clusterer.addMarkers(new_markers);
  }

}

    
var populateMapByIncident = function(incident, page, old_markers) {
  var run_again = false;
  var phase_number = GetUrlValue("phase_number")
  $.getJSON(
    "/api/private_map_handler",
    {"shortname" : incident, "page": page, "phase_number": phase_number},
    function(sites_list) {
    if (sites_list.length > 99) {
      run_again = true;
    }
    console.log(sites_list);
          var mapOptions = {
    zoom: 8,
    center: new google.maps.LatLng(40.6501038, -73.8495823),
    mapTypeId: google.maps.MapTypeId.ROADMAP
    }
//     var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
       var markers = [];
       var i = 0;
       
       for (var i = 0; i < sites_list.length; i++) {
	 var details = getInfoboxDetails(sites_list[i]);
	 var latLng = new google.maps.LatLng(sites_list[i].latitude, sites_list[i].longitude);
	 var marker = new google.maps.Marker({'position': latLng, 
					     'icon': getMarkerIcon(sites_list[i]), 
					     'site_id': sites_list[i].id, 
					     'site_info': sites_list[i],
	});
	 markers.push(marker);
	 var site_id = sites_list[i].id;
	
	google.maps.event.addListener(marker, "click", function() {
	  var this_phase_id = this.site_info.phase_id;
	  console.log(this.site_info)

	  new Messi.load('/api/private_site_handler?case_number=' + this.site_info.case_number +'&phase_number=' + phase_number,
	  {title: 'Case Number: ' + this.site_info.case_number + '<br>Work Type: ' + this.site_info.work_type, titleClass: 'info'});

	});
       }
       
       	  var total_markers = old_markers.concat(markers)
	         clusterer.addMarkers(total_markers);
	  all_markers = old_markers.concat(markers);
       $("#display_incident").text("Incident: " + incident);

         if (run_again == true) {
	    populateMapByIncident(incident, page + 1, total_markers);
	} else {

	  var total_markers = old_markers.concat(markers);
	         clusterer.addMarkers(total_markers);
	}
       
    }
  );

}


function GetUrlValue(VarSearch){
    var SearchString = window.location.search.substring(1);
    var VariableArray = SearchString.split('&');
    for(var i = 0; i < VariableArray.length; i++){
        var KeyValuePair = VariableArray[i].split('=');
        if(KeyValuePair[0] == VarSearch){
            return KeyValuePair[1];
        }
    }
}

var getInfoboxDetails = function(site) {
 details = "";
 for (var i in site) {
        if (details.length > 100000) break;
        if (i == "initials of resident present" ||
            i == "address" ||
            i == "city" ||
            i == "status" ||
            i == "clustered" ||
            i == "zip_code" ||
            i == "case_number" ||
            i == "name" ||
            i == "request_date" ||
            i == "prepared_by" ||
            i == "state" ||
            i == "county" ||
            i == "cross_street" ||
            i == "rent_or_own" ||
            i == "time_to_call" ||
            i == "phone1" ||
            i == "phone2" ||
            i == "name_metaphone" ||
            i == "address_digits" ||
            i == "address_metaphone" ||
            i == "city_metaphone" ||
            i == "phone_normalised" ||
            i == "event" ||
            i == "hours_worked_per_volunteer" ||
            i == "claim_for_org" ||
            i == "initials_of_resident_present" ||
            i == "status_notes" ||
            i == "total_volunteers" ||
            i == "rent_or_own" ||
            i == "work_without_resident" ||
            i == "status" ||
            i == "total_volunteers" ||
            i == "prepared_by" ||
            i == "email1" ||
            i == "email2" ||
            i == "temporary_address"
            
        ) continue;
        var label = i.replace(/_/g, " ");
        label = label[0].toUpperCase() + label.slice(1);
        if (i == "habitable") {
            if (!site[i]) {
                details += "House is not habitable. ";
            }
        } else if (typeof site[i] == "string" && site[i].length > 0 && site[i] != "n") {
	    if (label != "Event name" && site[i] != "0") {
	      details += label + ": " + site[i];
	      if (details[details.length - 1] != ".") details += ". ";
	    }
        }
    }
    console.log(details);
    return details;
}

var getMarkerIcon = function (site) {
    // TODO(Jeremy): Do we really want them invisible? Wouldn't it be better to
    // Just remove them from the database in this case?
    if (kCompletionStatusColors[site["status"]] == "invisible") {
        return null;
    }
    var color = "red";
    if (site["claimed_by"] !== null &&
        site["status"] == "Open, unassigned") {
        color = "orange";
    } else {
        color = kCompletionStatusColors[site["status"]] || "red";
    }

    var marker_work_type = "Unknown";
    if (site.derechos_work_type && site.derechos_work_type != "None") {
        marker_work_type = site.derechos_work_type;
    } else if (site.work_type && site.work_type != "None") {
        marker_work_type = site.work_type;
    }
    site.work_type = marker_work_type;
    var icon_type = site.work_type.replace(/ /g, "_");
    console.log("/icons/" + icon_type + "_" + color + ".png");
    console.log(site.work_type);
    return "/icons/" + icon_type + "_" + color + ".png";
}

var kCompletionStatusColors = {
    "Open, unassigned":"red",
    "Open, assigned":"yellow",
    "Open, partially completed":"yellow",
    "Closed, completed":"green",
    "Closed, incomplete":"green",
    "Closed, out of scope":"gray",
    "Closed, done by others":"green",
    "Closed, rejected":"xgray",
    "Open, needs follow-up":"yellow",
    "Closed, duplicate":"xgray",
    "Closed, no help wanted":"xgray"
};


function OpenInNewTab(url )
{
  var win=window.open(url, '_blank');
  win.focus();
}