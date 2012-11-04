goog.require('goog.dom');
goog.require('goog.ui.Dialog');

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

function AddMarker(lat, lng, site, map, infowindow) {
  var marker = new google.maps.Marker({
    position: new google.maps.LatLng(lat, lng),
    map: map,
    title: site.name,
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
      dialog.setButtonSet(goog.ui.Dialog.ButtonSet.OK);
    }
    dialog.setVisible(false);
    dialog.setContent("<h2>" + site["name"] + "</h2>" + "<a href='/edit?id=" + site["id"] + "'>Edit</a><br />" + "Address: " + site["address"] + " " + site["city"] + "<br/>" + "Requests: " + site["work_requested"] + "<br/>");
    dialog.setTitle(site["name"]);
    goog.events.listen(dialog, goog.ui.Dialog.EventType.SELECT, function(e) {});

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
