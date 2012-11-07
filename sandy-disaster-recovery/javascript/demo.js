goog.require('goog.dom');
goog.require('goog.events.EventType');
goog.require('goog.string');
goog.require('goog.ui.Dialog');
goog.require('goog.ui.Dialog.ButtonSet');
goog.require('goog.ui.Option');
goog.require('goog.ui.Select');
goog.require('sandy.map');

goog.provide('sandy.demo');

var dialog;

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
  marker["site"] = site;
  marker["tags"] = sandy.map.ClassifySite(site);
  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent(
        "<h2 class='unauthenticated_header'>Unauthenticated</h2><p class='unauthenticated_note'>This version of the map only contains " +
        "approximate latitude and longitude, and Street View is not provided.  In addition, " +
        "all personal details have been removed. </p>" +
        "<p class='please_log_in'>Please log in to view details. <a href='/authentication?destination=/dev/map'>Authenticate</a></p>");
    infowindow.open(map, marker);
  });
  return marker;
}

sandy.demo.initialize = function() {
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
}
