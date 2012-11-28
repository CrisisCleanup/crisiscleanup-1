/**
 * Copyright 2012 Jeremy Pack
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/
goog.require("goog.dom");

goog.require('goog.dom');
goog.require('goog.ui.ac.ArrayMatcher');
goog.require('goog.ui.ac.AutoComplete');
goog.require('goog.ui.ac.InputHandler');
goog.require('goog.ui.ac.Renderer');
goog.require('goog.ui.ac');

goog.provide("sandy.form");


var map;
var geocoder;
var autocomplete;
sandy.form.Initialize = function() {
  var myLatlng = new google.maps.LatLng(40.7697, -73.5735);
  var mapOptions = {
    zoom: 11,
    center: myLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
  sandy.form.SetUpValidation();
}

sandy.form.SetUpValidation = function() {
  geocoder = new google.maps.Geocoder();
  // Set up validation events.
  goog.dom.getElement('address').onblur = validate;
  goog.dom.getElement('zip_code').onblur = validate;
  goog.dom.getElement('state').onblur = validate;
  goog.dom.getElement('county').onblur = validate;
  goog.dom.getElement('city').onblur = validate;
  var setToZero = [
      goog.dom.getElement('hours_worked_per_volunteer'),
      goog.dom.getElement('total_volunteers')];
  for (var i = 0; i < setToZero.length; ++i) {
    if (setToZero[i].value == "" || !setToZero[i].value) {
      setToZero[i].value = "0";
    }
  }
}


var last_city = "";
var last_state = "";
var last_zip_code = "";
var last_geocode = "";
var geocoding = false;
var marker;

function validate() {
  var zip_code = goog.dom.getElement('zip_code').value;
  var city_value = goog.dom.getElement('city').value;
  var state_value = goog.dom.getElement('state').value;
  var street_address = goog.dom.getElement('address').value;
  if ((zip_code.length < 5 && city_value.length < 2 && state_value.length < 2) ||
      street_address.length < 5) return;
  var address = street_address;
  // If city was not automatically set, then use it.
  if (city_value != last_city) {
    address += " " + city_value;
  }
  if (state_value != last_state) {
    address += " " + state_value;
  }
  if (zip_code != last_zip_code) {
    address += " " + zip_code;
  }
  address += " USA";
  if (address == last_geocode) return;
  last_geocode = address;

  geocoder.geocode({ 'address': address }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      ll = results[0].geometry.location;
      if (marker) marker.setMap(null);
      marker = new google.maps.Marker({
        map: map,
        position: ll
      });
      var mapBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(ll.lat() - .05, ll.lng() - .02),
	new google.maps.LatLng(ll.lat() + .05, ll.lng() + .08));
      map.setZoom(10);
      map.fitBounds(mapBounds);
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
          } else if (comps[i].types[t] === "postal_code") {
            var zip_code = goog.dom.getElement("zip_code");
            if (zip_code.value === last_zip_code) {
              zip_code.value = last_zip_code = comps[i].long_name;
              goog.dom.getElement("zipCodeSuggestion").innerHTML = "";
            } else if (zip_code.value !== comps[i].long_name) {
              goog.dom.getElement("zipCodeSuggestion").innerHTML = comps[i].long_name + "?";
            } else {
              goog.dom.getElement("zipCodeSuggestion").innerHTML = "";
            }
          } else if (comps[i].types[t] === "administrative_area_level_2") {
            goog.dom.getElement("county").value = comps[i].long_name;
          }
        }
      }
    } else {
      //alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}
