goog.require('goog.ui.ac');
goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.json');
goog.require('goog.net.XhrIo');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');
goog.require('goog.style');
goog.require('goog.dom.forms');
goog.require('sandy.map');
goog.require('sandy.form');

goog.provide('sandy.main');

var siteMap = {};
var autoComplete;
var dialog;
var sites;
var runSiteRpc = function(request, response_handler) {
  goog.net.XhrIo.send('/api/site', function(e) {
    var xhr = e.target;
    var status = xhr.getStatus();
    var response_text = xhr.getResponseText();
    if (response_handler !== undefined) {
      response_handler(status, response_text, xhr);
    }
  }, 'PUT', goog.json.serialize(request));
};

var claimSite = function(site_id, response_handler) {
  var request = {id: site_id, action: 'claim'}
  runSiteRpc(request, response_handler);
};

// fields is a field => value mapping.
var updateSiteFields = function(site_id, fields, response_handler) {
  var request = {id: site_id, action: 'update', update: fields};
  runSiteRpc(request, response_handler);
};

var setMessageHtml = function(message_html) {
  document.getElementById('message_div').innerHTML = message_html;
};

// Creates and returns a <select> DOM element populated with status choices.
// The site's current value is selected.
var createStatusSelect = function(site) {
  var status_select = document.createElement('select');
  var addOption = function (value) {
    var option = document.createElement('option');
    if (value == site['status']) {
      option.selected = true;
    }
    option.text = value;
    goog.dom.append(status_select, option);
  };
  var added_current_value = false;
  for(var i = 0; i < STATUS_CHOICES.length; i++) {
    var choice = STATUS_CHOICES[i];
    addOption(choice);
    if (choice == site['status']) {
      added_current_value = true;
    }
  }
  if (!added_current_value) {
    addOption(site['status']);
  }
  status_select.onchange = function(e) {
    var select = e.target;
    var new_value = select.value;
    setMessageHtml('working...');
    updateSiteFields(site['id'], {status: select.value},
      function(status, response_text, xhr) {
        if (status == 200) {
          setMessageHtml('Successfully changed status.');
          site["status"] = select.value;
	  site["tags"] = sandy.map.ClassifySite(site, my_organization);
	  var marker = site["marker"];
          if (marker) {
	    marker.icon = getMarkerIcon(site);
	  }
	  sandy.map.RefilterSingle(site);
        } else {
          setMessageHtml('Failure: ' + response_text);
        }
      });
    return false;
  };
  return status_select;
};

var currentEditSite;

sandy.main.SaveEdit = function() {
  var content = goog.dom.forms.getFormDataString(goog.dom.getElement("edit_form"));
  var site = currentEditSite;
  var onFormSubmit = function(e) {
    var xhr = e.target;
    var status = xhr.getStatus();
    if (status == 200) {
      sandy.main.CloseEdit();
    } else if (status == 400) {
      goog.dom.getElement("single_site").innerHTML = xhr.getResponseText();
    }
  }
  goog.net.XhrIo.send("/edit?mode=js&id=" + currentEditSite["id"],
		      onFormSubmit,
		      "POST",
                      content);

}

sandy.main.CloseEdit = function() {
  goog.style.showElement(goog.dom.getElement('form_background'), false);
  if (currentEditSite)
    sandy.main.SelectSite(currentEditSite);
  goog.style.showElement(goog.dom.getElement("legend_div"), true);
}

sandy.main.OpenEdit = function(site) {
  currentEditSite = site;
  goog.net.XhrIo.send('/edit?mode=js&id=' + site["id"],
		      function(e)
  {
    var xhr = e.target;
    var status = xhr.getStatus();
    if (status != 200) {
	return;
    }
    goog.style.showElement(goog.dom.getElement("legend_div"), false);
    goog.dom.getElement("single_site").innerHTML = xhr.getResponseText();
    var formBackground = goog.dom.getElement("form_background");
    dialog.setVisible(false);
    goog.style.showElement(formBackground, true);
    sandy.form.SetUpValidation();
  })
}

var kCompletionStatusColors = {
  "Open, unassigned" : "red",
  "Open, assigned": "yellow",
  "Open, partially Completed": "yellow",
  "Closed, completed": "green",
  "Closed, incomplete": "green",
  "Closed, out of Scope": "gray",
  "Closed, done by Others": "darkgreen",
  "Closed, rejected": "xgray",
  "Open, needs follow-up": "yellow",
  "Closed, duplicate": "invisible",
  "Closed, no help wanted": "invisible"
};

var getMarkerIcon = function(site) {
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
  site.work_type = site.work_type || "Unknown";
  var icon_type = site.work_type.replace(/ /g, "_");
  return "/icons/" + icon_type + "_" + color + ".png";
}

var dialogSite = null;
var updateSite = function(site) {
  var marker = site["marker"];
  // Schedule an update with XHR for this site.
  goog.net.XhrIo.send('/api/site_ajax?id=' + site.id,
		      function(e) {
    var xhr = e.target;
    var status = xhr.getStatus();
    if (status == 200) {
      var new_site = xhr.getResponseJson();
      for (var p in new_site) {
        site[p] = new_site[p];
	if (dialog_site == site) {
          updateDialogForSite(dialog, site);
	  site["tags"] = sandy.map.ClassifySite(site, my_organization);
	  sandy.map.RefilterSingle(site);
          var marker_icon = getMarkerIcon(site);
          if (marker) {
            if (marker_icon) {
              marker.setIcon(marker_icon);
              marker.setVisible(true);
            } else {
              marker.setVisible(false);
            }
          }
	}
      }
    }
  })
}

// Updates dialog content and event listeners for the given site.
var updateDialogForSite = function(dialog, site) {
  dialog_site = site;
  var main_div = document.createElement('div');
  var addField = function(label, value) {
    var div = document.createElement('div');
    div.innerHTML = "<b>" + goog.string.htmlEscape(label) + ":</b> ";
    if (typeof value == "string") {
      // Treat the value as a key into site.
      goog.dom.appendChild(div, document.createTextNode(value));
    } else {
      // Treat the value as a DOM element.
      goog.dom.appendChild(div, value);
    }
    goog.dom.appendChild(main_div, div);
  };

  var addButton = function(label, event_handler) {
    button = document.createElement('button');
    button.innerHTML = label;
    button.onclick = event_handler;
    goog.dom.appendChild(main_div, button);
  };

  dialog.setTitle("Case number: " + site["case_number"]);

  addField("Name", site["name"]);
  addField("Requests", site["work_requested"]);
  addField("Status", createStatusSelect(site));
  if (site.claimed_by !== null) {
    addField("Claimed by", site["claimed_by"]["name"]);
  }

  addButton('Printer Friendly', function(e) {
    window.open("/print?id=" + site["id"], '_blank');
  });
  addButton('Edit', function(e) {
    sandy.main.OpenEdit(site);
  });

  if (site.claimed_by === null) {
    addButton('Claim', function(e) {
      setMessageHtml('working...');
      claimSite(site['id'], function(status, response_text, xhr) {
        if (status == 200) {
          setMessageHtml('Succesfully claimed.');
	  updateSite(site);
        } else {
          if (response_text) {
            setMessageHtml('Failure: ' + response_text);
          } else {
            setMessageHtml('Failure: an unknown error occurred.');
          }
        }
      });
    });
  }

  var message_div = document.createElement('div')
  message_div.id = 'message_div';
  goog.dom.appendChild(main_div, message_div);
  dialog.setContent('');
  goog.dom.appendChild(dialog.getContentElement(), main_div);
};

function AddMarker(lat, lng, site, map, infowindow) {
  site["tags"] = sandy.map.ClassifySite(site, my_organization);
  var icon = getMarkerIcon(site);
  if (!icon) return null;
  var marker = new google.maps.Marker({
    position: new google.maps.LatLng(lat, lng),
    map: map,
    title: site.name,
    icon: icon
  });
  site["marker"] = marker;
  google.maps.event.addListener(marker, 'click', function() {
    sandy.main.SelectSite(site);
  });
  return marker;
}

var map;
var largeMarker = null;
sandy.main.SelectSite = function(site) {
  if (!dialog) {
    dialog = new goog.ui.Dialog();
    dialog.setModal(false);
    dialog.setDraggable(false);
    dialog.setButtonSet(null);
  }
  dialog.setVisible(false);
  updateDialogForSite(dialog, site);
  dialog.setVisible(true);
  dialog.getElement().style.left = null;
  dialog.getElement().style.top = null;
  dialog.getElement().style.right = "10px";
  dialog.getElement().style.bottom = "10px";
  updateSite(site);
  if (site["marker"]) {
    var location = site["marker"].getPosition();
    if (!map.getBounds().contains(location)) {
      map.panTo(location);
    }
  }
}

sandy.main.initialize = function() {
  var myLatlng = new google.maps.LatLng(39.483351, -74.999737);
  var mapOptions = {
    zoom: 8,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  goog.style.showElement(goog.dom.getElement('filtersbackground'), false);
  map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
  // TODO(Jeremy): Set myLatLng to the location of the highest
  // priority current site.
  var terms = [];
  var searchBox = goog.dom.getElement('search_box');
  autoComplete = goog.ui.ac.createSimpleAutoComplete(terms, searchBox, false);
  var selectFunction = function(e) {
    if (siteMap[e.row]) {
      var site = siteMap[e.row];
      sandy.main.SelectSite(site);
      searchBox.value = "";
      if (largeMarker) {
        largeMarker.setZIndex(0);
      }
      largeMarker = site["marker"];
      if (largeMarker) {
        largeMarker.setZIndex(5);
        largeMarker.setAnimation(google.maps.Animation.DROP);
        if (map.getZoom() < 8) {
            map.setZoom(8);
        }
        if (!map.getBounds().contains(largeMarker.getPosition())) {
            map.panTo(largeMarker.getPosition());
        }
      }
    }
  }
  searchBox.onchange = selectFunction;
  goog.events.listen(autoComplete,
		     goog.ui.ac.AutoComplete.EventType.UPDATE,
		     selectFunction);
  for (var i = 0; i < counties.length; ++i) {
  goog.net.XhrIo.send('/api/site_ajax?id=all&county=' + counties[i],
		      function(e) {
    var xhr = e.target;
    var status = xhr.getStatus();
    if (status == 200) {
      var sites = xhr.getResponseJson();
      sandy.map.InitializeMap(sites, AddMarker, map);
      var filters = goog.dom.getElement('filtersbackground');
      goog.style.showElement(filters, true);

      for (var i = 0; i < sites.length; ++i) {
        if (sites[i].case_number && sites[i].name) {
          var term = sites[i].case_number + ": <" + sites[i].name + ">";
          if (sites[i].address) {
            term += " " + sites[i].address;
          }
          if (sites[i].city) {
            term += " " + sites[i].city;
          }
          if (sites[i].state) {
            term += " " + sites[i].state;
          }
          if (sites[i].zip_code) {
            term += " " + sites[i].zip_code;
          }
          terms.push(term);
          siteMap[term] = sites[i];
        }
      }
    }
  })
  }
}
