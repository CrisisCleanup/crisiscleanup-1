
goog.provide('sandy.util');


var HOSTNAME_TO_COUNTRY = {
    // FQDN to ccTLD (*not* ISO 3166, because Google Maps uses ccTLDs)
    "www.crisiscleanup.org.au": 'au',
    "demo.crisiscleanup.org.au": 'au',
    "www.crisiscleanup.org.in": 'in',
    "demo.crisiscleanup.org.in": 'in'
};


sandy.util.MAP_CENTER = {
    'us': {'lat':  39.50, 'lon': -77.35},
    'au': {'lat': -25.96, 'lon': 136.23},
    'in': {'lat':  19.32, 'lon':  84.78}
};


sandy.util.COUNTRY_NAME = {
    'us': 'USA',
    'au': 'Australia',
    'in': 'India'
};


sandy.util.determineCountry = function() {
    if (HOSTNAME_TO_COUNTRY[window.location.hostname]) {
        return HOSTNAME_TO_COUNTRY[window.location.hostname];
    } else {
        return 'us';
    }
};
