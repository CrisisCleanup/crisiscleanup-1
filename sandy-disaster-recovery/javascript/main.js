goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');
goog.require('sandy.map');

goog.provide('sandy.main');

var dialog;
var panorama;

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
  return marker;
}

sandy.main.initialize = function() {
  var myLatlng = new google.maps.LatLng(39.483351, -74.999737);
  var mapOptions = {
    zoom: 4,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
  // TODO(rostovpack): Set myLatLng to the location of the highest
  // priority current site.
  sandy.map.InitializeMap(sites, AddMarker, map);
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
