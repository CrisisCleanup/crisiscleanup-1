goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');

var markers = [];
var panorama;

function classifySite(site) {
  var tags = [];
  tags.push(site["debris_removal_only"] ? "debris_only" : "not_only_debris");
  tags.push(site["electricity"] ? "electricity" : "no_electricty");
  tags.push(site["standing_water"] ? "standing_water" : "no_standing_water");
  tags.push(site["tree_damage"] ? "tree_damage" : "no_tree_damage");
  tags.push(site["habitable"] ? "habitable" : "not_habitable");
  tags.push(site["electrical_lines"] ? "electrial_lines" : "electrical_line_free");
  tags.push(site["cable_lines"] ? "phone_or_cable_lines" : "phone_or_cable_line_free");
  tags.push(site["cutting_cause_harm"] ? "trees_threaten_property" : "trees_dont_threaten_property");
  tags.push(site["work_type"]);
  tags.push(site["property_type"]);
  tags.push(site["state"]);
  return tags;
}

function refilter() {
  var els = document.getElementsByName("filter");
  var filters = [];
  for (var el = 0; el < els.length; ++el) {
    if (els[el].checked) filters.push(els[el].id);
  }
  for (var i = 0; i < markers.length; ++i) {
    var include = true;
    for (var f = 0; f < filters.length; ++f) {
      if (markers[i].tags.indexOf(filters[f]) === -1) {
        include = false;
        break;
      }
    }
    markers[i].setVisible(include);
  }
}
var dialog;

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
    // TODO(Bruce): Implement.
    var select = e.target;
    var new_value = select.value;
    alert("Change status hasn't been implemented yet.");
    return false;
  };
  return status_select;
};

// Updates dialog content and event listeners for the given site.
var updateDialogForSite = function(dialog, site) {
  var addField = function(label, value) {
    var div = document.createElement('div');
    div.innerHTML = "<b>" + goog.string.htmlEscape(label) + ":</b> ";
    if (typeof value == "string") {
      // Treat the value as a key into site.
      goog.dom.appendChild(div, document.createTextNode(site[value]));
    } else {
      // Treat the value as a DOM element.
      goog.dom.appendChild(div, value);
    }
    goog.dom.appendChild(dialog.getContentElement(), div);
  };

  dialog.setTitle("Case number: A" + site["id"]);

  dialog.setContent('');
  addField("Name", "name");
  addField("Requests", "work_requested");
  addField("Status", createStatusSelect(site));

  goog.events.listen(dialog, goog.ui.Dialog.EventType.SELECT, function(e) {
    var dialog = e.target;
    if (e.key == "edit") {
      window.location = "/edit?id=" + site["id"];
    } else if (e.key == "claim") {
      // TODO(Bruce): Implement.
      alert("Claiming hasn't been implemented yet.");
    }
    return false;
  });
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
  marker["tags"] = classifySite(site);
  markers.push(marker);
  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent("<h2>" + site["name"] + "</h2>" + "Address: " + site["address"] + " " + site["city"] + "<br/>" + "Requests: " + site["work_requested"] + "<br/>");
    // infowindow.open(map, marker);
    panorama.setPosition(marker.getPosition());
    panorama.setPov({
      heading: 0,
      pitch: 10,
      zoom: 1
    });
    infowindow.setZIndex(10);
    panorama.setVisible(true);
    if (!dialog) {
      dialog = new goog.ui.Dialog();
      dialog.setModal(false);
      dialog.setDraggable(false);
      var buttonSet = new goog.ui.Dialog.ButtonSet();
      buttonSet.addButton({caption: "Edit", key: "edit"});
      buttonSet.addButton({caption: "Claim", key: "claim"});
      dialog.setButtonSet(buttonSet);
    }
    dialog.setVisible(false);
    updateDialogForSite(dialog, site);
    dialog.setVisible(true);
    dialog.getElement().style.left = null;
    dialog.getElement().style.top = null;
    dialog.getElement().style.right = "10px";
    dialog.getElement().style.bottom = "10px";
  });
}

function initialize() {
  var myLatlng = new google.maps.LatLng(39.483351, -74.999737);
  var mapOptions = {
    zoom: 4,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);


  var infowindow = new google.maps.InfoWindow({
    content: ""
  });
  for (var i = 0; i < sites.length; ++i) {
    var site = sites[i];
    var lat = site["latitude"];
    var lng = site["longitude"];
    var good_ll = true;
    if (isNaN(lat) || isNaN(lng)) {
      good_ll = false;
    }
    if (good_ll) {
      AddMarker(lat, lng, site, map, infowindow);
    }
  }
  if (markers.length > 0) {
    var min_lat = markers[0].getPosition().lat();
    var max_lat = min_lat;
    var min_lng = markers[0].getPosition().lng();
    var max_lng = min_lng;
    // Note that this code may completely break for those
    // hurricane victims near the international date line.
    for (var i = 1; i < markers.length; ++i) {
      var ll = markers[i].getPosition();
      min_lat = Math.min(min_lat, ll.lat());
      min_lng = Math.min(min_lng, ll.lng());
      max_lat = Math.max(max_lat, ll.lat());
      max_lng = Math.max(max_lng, ll.lng());
    }
    map.fitBounds(new google.maps.LatLngBounds(
        new google.maps.LatLng(min_lat - .001, min_lng - .001), 
        new google.maps.LatLng(max_lat + .001, max_lng + .001)));
  }
  if (markers.length > 0) myLatlng = markers[0].getPosition();
  var panoramaOptions = {
    position: myLatlng,
    pov: {
      heading: 0,
      pitch: 10,
      zoom: 1
    }
  };
  panorama = new google.maps.StreetViewPanorama(document.getElementById("pano"), panoramaOptions);
  map.setStreetView(panorama);
}


function sayHi() {
  var newHeader = goog.dom.createDom(
    'h1',
    { 'style': 'background-color:#EEE' },
    'Hello world!');
  goog.dom.appendChild(document.body, newHeader);
}
