goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.json');
goog.require('goog.net.XhrIo');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');
goog.require('sandy.map');

goog.provide('sandy.main');

var dialog;

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
var createStatusSelect = function(site, marker) {
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
	  marker["tags"] = sandy.map.ClassifySite(site, my_organization);
	  sandy.map.Refilter();
        } else {
          setMessageHtml('Failure: ' + response_text);
        }
      });
    return false;
  };
  return status_select;
};

var dialogSite = null;
var updateSite = function(site, marker) {
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
          updateDialogForSite(dialog, site, marker);
	  marker["tags"] = sandy.map.ClassifySite(site, my_organization);
	  sandy.map.Refilter();
	}
      }
    }
  })
}

// Updates dialog content and event listeners for the given site.
var updateDialogForSite = function(dialog, site, marker) {
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
  addField("Status", createStatusSelect(site, marker));
  if (site.claimed_by !== null) {
    addField("Claimed by", site["claimed_by"]["name"]);
  }

  addButton('Printer Friendly', function(e) {
    window.open("/print?id=" + site["id"], '_blank');
  });
  addButton('Edit', function(e) {
    window.location = "/edit?id=" + site["id"];
  });

  if (site.claimed_by === null) {
    addButton('Claim', function(e) {
      setMessageHtml('working...');
      claimSite(site['id'], function(status, response_text, xhr) {
        if (status == 200) {
          setMessageHtml('Succesfully claimed.');
	  updateSite(site, marker);
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
  function siteToIconUrl(site) {
    if (!site.work_type) {
      return '/icons/darkred-dot.png';
    }
    var url = '/icons/' + site.work_type + '_';
    var now = new Date();
    var TWO_DAYS_IN_MSEC = 172800000;
    if (!site.habitable) {
      url += 'red.png';
    } else if (now - new Date(site.request_date) > TWO_DAYS_IN_MSEC) {
      url += 'orange.png';
    } else {
      url += 'green.png';
    }
    return url;
  }
  var marker = new google.maps.Marker({
    position: new google.maps.LatLng(lat, lng),
    map: map,
    title: site.name,
    icon: new google.maps.MarkerImage(siteToIconUrl(site))
  });
  marker["tags"] = sandy.map.ClassifySite(site, my_organization);
  marker["site"] = site;
  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent("<h2>" + site["name"] + "</h2>" + "Address: " + site["address"] + " " + site["city"] + "<br/>" + "Requests: " + site["work_requested"] + "<br/>");
    infowindow.setZIndex(10);
    if (!dialog) {
      dialog = new goog.ui.Dialog();
      dialog.setModal(false);
      dialog.setDraggable(false);
      dialog.setButtonSet(null);
    }
    dialog.setVisible(false);
    updateDialogForSite(dialog, site, marker);
    dialog.setVisible(true);
    dialog.getElement().style.left = null;
    dialog.getElement().style.top = null;
    dialog.getElement().style.right = "10px";
    dialog.getElement().style.bottom = "10px";
    updateSite(site, marker);
  });
  return marker;
}

sandy.main.initialize = function() {
  var myLatlng = new google.maps.LatLng(39.483351, -74.999737);
  var mapOptions = {
    zoom: 10,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
  // TODO(Jeremy): Set myLatLng to the location of the highest
  // priority current site.
  sandy.map.InitializeMap(sites, AddMarker, map);
}
