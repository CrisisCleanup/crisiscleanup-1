goog.require("goog.dom");

var map;
var geocoder;

function initialize() {
  geocoder = new google.maps.Geocoder();
  var myLatlng = new google.maps.LatLng(39.483351, -74.999737);
  var mapOptions = {
    zoom: 8,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

  // Set up validation events.
  goog.dom.getElement('address').onblur = validate;
  goog.dom.getElement('zip_code').onblur = validate;
}


var last_city = "";
var last_state = "";
var geocoding = false;
var marker;

function validate() {
  var address = goog.dom.getElement('address').value + " " + goog.dom.getElement('zip_code').value + " USA";
  geocoder.geocode({ 'address': address }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      ll = results[0].geometry.location;
      if (marker) marker.setMap(null);
      marker = new google.maps.Marker({
        map: map,
        position: ll
      });
      goog.dom.getElement('latitude').value = ll.lat();
      goog.dom.getElement('longitude').value = ll.lng();
      var comps = results[0].address_components;
      for (var i = 0; i < comps.length; ++i) {
        for (var t = 0; t < comps[i].types.length; ++t) {
          if (comps[i].types[t] === "administrative_area_level_1") {
            var state = goog.dom.getElement("state");
            if (state.value === last_state) {
              state.value = last_state = comps[i].short_name;
              goog.dom.getElement("stateSuggestion").innerHTML = "";
            } else if (state.value != comps[i].short_name) {
              goog.dom.getElement("stateSuggestion").innerHTML = comps[i].short_name + "?";
            } else {
              goog.dom.getElement("stateSuggestion").innerHTML = "";
            }
          } else if (comps[i].types[t] === "locality") {
            var city = goog.dom.getElement("city");
            if (city.value === last_city) {
              city.value = last_city = comps[i].long_name;
              goog.dom.getElement("citySuggestion").innerHTML = "";
            } else if (city.value !== comps[i].long_name) {
              goog.dom.getElement("citySuggestion").innerHTML = comps[i].long_name + "?";
            } else {
              goog.dom.getElement("citySuggestion").innerHTML = "";
            }
          }
        }
      }
    } else {
      //alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}
