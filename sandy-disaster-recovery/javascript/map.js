goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');

goog.provide('sandy.map');

var markers = [];
var panorama;
var layerObjects = [];
var mapSites;

var layers = [
    { kml: "https://www.google.com/maps/ms?authuser=0&vps=3&ie=UTF8&msa=0&output=kml&msid=210988455284977221384.0004cdd5426e591f0780f",
      description: "Command Centers" },
    { kml: "https://www.google.com/maps/ms?ie=UTF8&authuser=0&msa=0&output=kml&msid=210988455284977221384.0004cdd57d7e7e61d9c00",
      description: "Affected Areas" },
              ];

sandy.map.ClassifySite = function(site, my_organization) {
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
  tags.push(site["state"]);
  if (!site.claimed_by) {
    tags.push("unclaimed");
  } else if (my_organization == site.claimed_by.name) {
    tags.push("claimed");
  }
  if (site.reported_by && site.reported_by.name == my_organization) tags.push("reported");
  if (site.status.indexOf("Open") >= 0) {
    tags.push("open");
  } else {
    tags.push("closed");
  }
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

sandy.map.InitializeMap = function(currentMapSites, AddMarker, map) {
  mapSites = currentMapSites;
  // Initialize KML layers
  for (var i = 0; i < layers.length; ++i) {
    var layer = new google.maps.KmlLayer({
       clickable: true,
       map: map,
       preserveViewport: true,
       suprressInfoWindows: false,
       url: layers[i].kml,
        });
    layerObjects.push(layer);
  }

  var infowindow = new google.maps.InfoWindow({
    content: ""
  });
  for (var i = 0; i < mapSites.length; ++i) {
    var site = mapSites[i];
    var lat = site["latitude"];
    var lng = site["longitude"];
    var good_ll = true;
    if (isNaN(lat) || isNaN(lng)) {
      good_ll = false;
    }
    if (good_ll) {
      markers.push(AddMarker(lat, lng, site, map, infowindow));
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
}
