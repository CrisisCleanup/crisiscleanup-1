
import json
import urllib2

def geocode(address):
    """
    Geocode @address using the Google Maps API.

    Runs server-side so has a usage limit.

    No caching at present.
    """
    url = (
        "http://maps.google.com/maps/api/geocode/json?"
        "address=%s&sensor=false" % urllib2.quote(address)
    )
    response = json.loads(urllib2.urlopen(url).read())
    if response['status'] == 'OVER_QUERY_LIMIT':
        raise OverQuotaError()
    elif response['status'] == 'ZERO_RESULTS':
        result = None
    elif response['status'] == 'OK':
        result = response['results'][0]
    else:
        raise Exception(response)
    return result
