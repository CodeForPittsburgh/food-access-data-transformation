"""
Helper for retrieving Long/Lat from Map Box API.
"""

import requests


SERVICE_ADDRESS = 'https://api.mapbox.com/geocoding/v5/mapbox.places/$search.json'


def get_coordinates(key: str, address: str) -> dict | None:
    """
    Returns an object with the longitude and latitude

    Args:
        key (str): API Key
        address (str): Address to search for

    Returns:
        dict: Dictionary containing Long/Lat.
    """

    if key and address:
        url = SERVICE_ADDRESS.replace('$search', address)
        params = {'access_token': key, 'limit': 1, 'types': 'address'}

        response = requests.get(url, params=params, timeout=60)

        if response.status_code == 200:
            body = response.json()
            for feature in body['features']:
                result = get_geo_value(feature, 'address')
                if result:
                    return result
    return None


def get_geo_value(feature: dict, type: str) -> dict | None:
    """
    Returns the Geometry of the location based on provided type.

    Args:
        feature (dict): Feature from the response to check
        type (str): Type of feature to find

    Returns:
        dict: Coordinates
    """

    if 'place_type' in feature and type in feature['place_type'] and 'center' in feature:
        geo = feature['center']
        return {
            'longitude': geo[0],
            'latitude': geo[1]
        }
