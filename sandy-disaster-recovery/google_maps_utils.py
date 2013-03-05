
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

def geocoding_to_address_dict(geocoding):
    """
    >>> f = geocoding_to_address_dict
    >>> r = {u'address_components': [{u'long_name': u'15',
    ...     u'short_name': u'15',
    ...     u'types': [u'street_number']},
    ...    {u'long_name': u'Park Avenue',
    ...     u'short_name': u'Park Ave',
    ...     u'types': [u'route']},
    ...    {u'long_name': u'Midtown',
    ...     u'short_name': u'Midtown',
    ...     u'types': [u'neighborhood', u'political']},
    ...    {u'long_name': u'Manhattan',
    ...     u'short_name': u'Manhattan',
    ...     u'types': [u'sublocality', u'political']},
    ...    {u'long_name': u'New York',
    ...     u'short_name': u'New York',
    ...     u'types': [u'locality', u'political']},
    ...    {u'long_name': u'New York',
    ...     u'short_name': u'New York',
    ...     u'types': [u'administrative_area_level_2', u'political']},
    ...    {u'long_name': u'New York',
    ...     u'short_name': u'NY',
    ...     u'types': [u'administrative_area_level_1', u'political']},
    ...    {u'long_name': u'United States',
    ...     u'short_name': u'US',
    ...     u'types': [u'country', u'political']},
    ...    {u'long_name': u'10016',
    ...     u'short_name': u'10016',
    ...     u'types': [u'postal_code']}],
    ...   u'formatted_address': u'15 Park Avenue, New York, NY 10016, USA',
    ...   u'geometry': {u'location': {u'lat': 40.74741909999999, u'lng': -73.9807988},
    ...    u'location_type': u'ROOFTOP',
    ...    u'viewport': {u'northeast': {u'lat': 40.74876808029149,
    ...      u'lng': -73.97944981970849},
    ...     u'southwest': {u'lat': 40.74607011970849, u'lng': -73.9821477802915}}},
    ...   u'types': [u'street_address']}
    >>> f(r) 
    {'city': u'New York', 'longitude': -73.9807988, 'county': u'New York', 'state': u'NY', 'address': u'15 Park Ave', 'latitude': 40.74741909999999, 'zip_code': u'10016'}
    """
    ad = {
        'address': None, 
        'city': None,
        'county': None,
        'state': None,
        'zip_code': None,
        'latitude': None,
        'longitude': None
    }
    for comp in geocoding.get('address_components', []):
        types = comp['types']
        if 'street_number' in types:
            ad['address'] = comp['long_name']
        elif 'route' in types:
            ad['address'] = (
                (ad['address'] + ' ' if ad['address'] else '') + comp['short_name']
            )
        elif 'locality' in types:
            ad['city'] = comp['long_name']
        elif 'administrative_area_level_2' in types:
            ad['county'] = comp['long_name']
        elif 'administrative_area_level_1' in types:
            ad['state'] = comp['short_name']
        elif 'postal_code' in types:
            ad['zip_code'] = comp['long_name']
    if geocoding.get('geometry', None) and geocoding['geometry'].get('location', None):
        ad['latitude'] = geocoding['geometry']['location']['lat']
        ad['longitude'] = geocoding['geometry']['location']['lng']
    return ad


