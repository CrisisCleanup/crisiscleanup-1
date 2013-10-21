
goog.provide('sandy.util');


var HOSTNAME_TO_COUNTRY = {
    "www.crisiscleanup.org.au": 'au',
    "www.crisiscleanup.org.in": 'in'
};


sandy.util.MAP_CENTER = {
    'us': new google.maps.LatLng( 39.50, -77.35),
    'au': new google.maps.LatLng(-25.96, 136.23),
    'in': new google.maps.LatLng( 19.32,  84.78)
};


sandy.util.determineCountry = function() {
    if (HOSTNAME_TO_COUNTRY[window.location.hostname]) {
        return HOSTNAME_TO_COUNTRY[window.location.hostname];
    } else {
        return 'us';
    }
};
