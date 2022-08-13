"""
Unit Tests for the MapBox Helper.
"""


import responses

from data_scripts.helpers import mapbox
from urllib import parse
from assertpy import assert_that
import json


# Global items that are used in all tests.
ADDRESS = parse.quote('106 27th Ave, Altoona, Pa, 16601')
API_KEY = 'MYKEY'
URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + ADDRESS + \
    '.json?access_token=' + API_KEY + '&limit=1&types=address'


def get_response_file() -> dict:
    """
    Returns the Map Box Response JSON.

    Returns:
        str: JSON of Map Box Response
    """
    with open('./tests/helper_tests/map-box-response.json', 'r', encoding='utf-8') as input_file:
        return json.load(input_file)


@responses.activate
def test_get_cordinates():
    """
    Tests retrieving Coordinates successfully.
    """

    response_json = get_response_file()

    resp = responses.Response(
        method="GET",
        url=URL,
        status=200,
        json=response_json
    )
    responses.add(resp)

    result = mapbox.get_coordinates(API_KEY, ADDRESS)

    assert_that(result, 'Result should contain the Long/Lat of -78.41051, 40.52806').is_equal_to(
        {'longitude': -78.41051, 'latitude': 40.52806})


def test_get_coordinates_no_key():
    """
    Tests retrieving coordinates without an API Key.
    """

    result = mapbox.get_coordinates(None, ADDRESS)
    assert_that(result, 'No Api Key should result in None').is_none()


def test_get_coordinates_no_address():
    """
    Tests retrieving coordinates without an 
    """

    result = mapbox.get_coordinates(API_KEY, None)
    assert_that(result, 'No Address should result in None').is_none()


@responses.activate
def test_get_coordinates_no_response():
    """
    Test retrieving coordinates without a response.
    """

    resp = responses.Response(
        method="GET",
        url=URL,
        status=500
    )
    responses.add(resp)
    result = mapbox.get_coordinates(API_KEY, None)
    assert_that(result, 'Errored Response should return None').is_none()
