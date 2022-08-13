"""
Test for the ArcGis Helper.
"""

import json
import re

import responses
from assertpy import assert_that
from data_scripts.helpers import gis
from responses import matchers

FMNP_RESPONSE_JSON = './tests/helper_tests/fmnp-response.json'
GPCFB_RESPONSE = './tests/helper_tests/gpcfb-response.json'
SNAP_RESPONSE = './tests/helper_tests/snap-response.json'
USDA_RESPONSE = './tests/helper_tests/usda-response.json'
VENDOR_RESPONSE = './tests/helper_tests/vendor-response.json'
WIC_RESPONSE = './tests/helper_tests/wic-response.json'
GOOGLE_SHEET_RESPONSE = './tests/helper_tests/google-sheet-response.txt'

GIS_SERVICE_1_URL = 'https://services1.arcgis.com'
GIS_SERVICE_5_URL = 'https://services5.arcgis.com'
WIC_URL = 'https://www.pawic.com'
GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/export'

def get_response(path:str) -> dict:
    """
    Loads the GIS Response to a String
    """

    with open(path, 'r', encoding='utf-8') as input_file:
        return json.loads(input_file.read())


@responses.activate
def test_get_fmnp_markets():
    """
    Tests retrieving results from a GIS Query.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")
    params = {
        'where': "FarmMarketCounty='Allegheny'",
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'resultType': 'none',
        'distance': '0.0',
        'units': 'esriSRUnit_Meter',
        'outFields': '*',
        'returnGeometry': 'true',
        'featureEncoding': 'esriDefault',
        'multipatchOption': 'xyFootprint',
        'returnExceededLimitFeatures': 'true',
        'sqlFormat': 'none',
        'f': 'pjson'
    }
    
    
    json_response = get_response(FMNP_RESPONSE_JSON)
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])
    responses.add(resp)
    
    result = gis.get_fmnp_markets()

    assert_that(result, '2 Results should be returned').is_length(2)

    assert_that(result[0], 'Id should be 139').contains_entry({'OBJECTID': 228314})


@responses.activate
def test_get_fmnp_markets_no_response():
    """
    Tests retrieving GIS Data with no results.
    """
    json_response = get_response(FMNP_RESPONSE_JSON)
    json_response['features'] = []
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")

    resp = responses.Response('GET', rx, json=json_response, status=200)
    responses.add(resp)

    result = gis.get_fmnp_markets()

    assert_that(result, 'No items should be returned').is_empty()


@responses.activate
def test_get_fmnp_markets_error():
    """
    Tests retreiving GIS Data with 500 response.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")

    json_response = get_response(FMNP_RESPONSE_JSON)
    resp = responses.Response('GET', rx, json=json_response, status=500)

    responses.add(resp)

    result = gis.get_fmnp_markets()

    assert_that(result, 'Result should be empty').is_empty()


@responses.activate
def test_get_wic_sites():
    """
    Tests retrieving Data for the WIC Sites
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{WIC_URL}*")    
    json_response = get_response(WIC_RESPONSE)
    
    resp = responses.Response('POST', rx, json=json_response, status=200, match=[matchers.json_params_matcher({"county":"2","zip":"","miles":"5"})])

    responses.add(resp)
    
    results = gis.get_wic_sites()
    
    assert_that(results, 'WIC Sites should not be empty').is_not_empty()
    assert_that(results[0], 'First Entry should be Shop N Save').contains_entry({'StoreName': 'Bethel Park Shop N Save'})

@responses.activate
def test_get_wic_sites_no_results():
    """
    Tests no result sreturned for the WIC sites.
    """
    

    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{WIC_URL}*")

    json_response = get_response(WIC_RESPONSE)
    json_response['d'] = ''
    
    
    resp = responses.Response('POST', rx, json=json_response, status=200)

    responses.add(resp)
    
    results = gis.get_wic_sites()
    assert_that(results, 'WIC Results should be empty').is_empty()
    
@responses.activate
def test_get_wic_sites_error():
    """
    Tests an Error is returned retrieving the WIC Sites.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{WIC_URL}*")

    json_response = get_response(WIC_RESPONSE)
    
    resp = responses.Response('POST', rx, json=json_response, status=500)

    responses.add(resp)
    
    results = gis.get_wic_sites()
    assert_that(results, 'WIC Sites should be empty').is_empty()

@responses.activate
def test_get_snap_sites():
    """
    Tests Retrieving SNAP Sites.
    """

    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")
    params = {
        'where': "State = 'PA' AND County = 'ALLEGHENY'",
        'outFields':'*',
        'outSR': '4326',
        'f': 'json'
    }

    json_response = get_response(SNAP_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_snap_sites()
    assert_that(results, 'SNAP Sites should not be empty').is_not_empty()
    assert_that(results[0], 'Object ID 105 should be returned').contains_entry({'ObjectId': 105})

@responses.activate
def test_get_snap_sites_no_results():
    """
    Tests retrieving no results from the SNAP Sites.
    """

    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(SNAP_RESPONSE)
    json_response['features'] = []
    
    resp = responses.Response('GET', rx, json=json_response, status=200)

    responses.add(resp)
    
    results =gis.get_snap_sites()
    assert_that(results, 'SNAP results should be empty').is_empty()
    
@responses.activate
def test_get_snap_sites_error():
    """
    Tests an error occuring during SNAP Site retrieval.
    """

    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(SNAP_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=500)

    responses.add(resp)
    
    results = gis.get_snap_sites()
    assert_that(results, 'SNAP Sites should be empty').is_empty()

@responses.activate   
def test_get_gpcfb_sites():
    """
    Tests retrieving the Greater PGH Food Bank Sites.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")
    params = {
        'where': '1=1',
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'resultType': 'none',
        'distance':'0.0',
        'units': 'esriSRUnit_Meter',
        'outFields': '*',
        'returnGeometry': 'true',
        'featureEncoding': 'esriDefault',
        'multipatchOption': 'xyFootprint',
        'returnExceededLimitFeatures': 'true',
        'sqlFormat':'none',
        'f':'pjson'
    }

    json_response = get_response(GPCFB_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_gpcfb_sites()
    
    assert_that(results, 'GPCFB Sites should not be empty').is_not_empty()
    
    assert_that(results[0], 'First Entry should contain objectid 139')\
        .contains_entry({'objectid': 139})\
        .contains_entry({'longitude': -80.0007569578037})\
        .contains_entry({'latitude': 40.478952041312951})

@responses.activate  
def test_get_gpcfb_sites_no_results():
    """
    Tests no results returned for Greater PGH Food Bank Sites.
    """

    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(GPCFB_RESPONSE)
    json_response['features'] = []
    resp = responses.Response('GET', rx, json=json_response, status=200)

    responses.add(resp)
    
    results = gis.get_gpcfb_sites()
    
    assert_that(results, 'GPCFB Sites should be empty').is_empty()

@responses.activate    
def test_get_gpcfb_sites_error():
    """
    Tests an error is returned for Greater PGH Food bank sites.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(GPCFB_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=500)

    responses.add(resp)
    
    results = gis.get_gpcfb_sites()
    
    assert_that(results, 'GPCFB Results should be empty').is_empty()
    
@responses.activate  
def test_get_schedule_enty():
    """
    Tests retrieving a Vendor Schedule
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")
    params = {
        'where': "FarmMarketID='11445566'",
        'resultType': 'none',
        'outFields': '*',
        'sqlFormat': 'none',
        'f': 'pjson'
    }

    json_response = get_response(VENDOR_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_schedule_entry('11445566')
    
    assert_that(results, 'Vendor response should not be None').is_not_none()
    
    assert_that(results, 'Only the Vendor Schedule should be in the list').contains('July - October Tuesday - Sunday 12:00 PM - 5:30 PM')

@responses.activate     
def test_get_schedule_entry_no_results():
    """
    Tests no results returned for Market Id
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")

    json_response = get_response(VENDOR_RESPONSE)
    json_response['features'] = []
    
    resp = responses.Response('GET', rx, json=json_response, status=200)

    responses.add(resp)
    
    results = gis.get_schedule_entry('223344')
    
    assert_that(results, 'Vendor schedule should be None').is_empty()

@responses.activate    
def test_get_schedule_entry_error():
    """
    Tests Error is returned for the Schedule Entry Retrieval
    """
    
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_5_URL}*")

    json_response = get_response(VENDOR_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=500)

    responses.add(resp)
    
    results = gis.get_schedule_entry('223344')
    
    assert_that(results, 'Vendor results should be None').is_empty()

@responses.activate    
def test_get_summer_meal_sites():
    """
    Tests retrieving the Summer meal sites from the USDA.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")
    params = {
        'outFields': '*',
        'where': "Site_State='PA' and Site_County='Allegheny'",
        'f': 'geojson'
    }
    json_response = get_response(USDA_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_summer_meal_sites()
    
    assert_that(results, 'Vendor response should not be empty').is_not_empty()
    
    assert_that(results[0], 'OBJECT ID should be 22').contains_entry({'OBJECTID': 22})

@responses.activate
def test_get_summer_meal_sites_long_lat():
    """
    Tests retrieving the Summer Meal Sites with missing Latitude and Longitude.
    """
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")
    params = {
        'outFields': '*',
        'where': "Site_State='PA' and Site_County='Allegheny'",
        'f': 'geojson'
    }
    json_response = get_response(USDA_RESPONSE)
    json_response['features'][0]['properties']['Latitude'] = None
    json_response['features'][0]['properties']['Longitude'] = None
    
    resp = responses.Response('GET', rx, json=json_response, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_summer_meal_sites()
    
    assert_that(results[0])\
        .contains_entry({'Longitude': -79.1447083721001})\
        .contains_entry({'Latitude': 40.6327814588326})

@responses.activate
def test_get_summer_meal_sites_no_results():
    """
    Tests no results retrieved from the Summer Meal sites.
    """    
    
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(USDA_RESPONSE)
    json_response['features'] = []
    resp = responses.Response('GET', rx, json=json_response, status=200)

    responses.add(resp)
    
    results = gis.get_summer_meal_sites()
    
    assert_that(results, 'Summer Meal Sites should be empty').is_empty()

@responses.activate    
def test_get_summer_meal_sites_error():
    """
    Tests Error returned from Summer Meal Sites request.
    """
    
    
    # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GIS_SERVICE_1_URL}*")

    json_response = get_response(USDA_RESPONSE)
    
    resp = responses.Response('GET', rx, json=json_response, status=500)

    responses.add(resp)
    
    results = gis.get_summer_meal_sites()
    
    assert_that(results, 'Summer Meal sites should be empty').is_empty()
    
@responses.activate
def test_get_google_spreadsheet():
    """
    Tests Retrieving a Google Spreadsheet and converting to List of Dictionaryies
    """
    
        # regex that matches the url and ignores anything that comes after
    rx = re.compile(rf"{GOOGLE_SHEET_URL}*")
    
    params = {
        'id': '1QwWXDMzNc7X-krErCwuzTHgXfiru-U99jJeJ6nk9hko',
        'exportFormat': 'csv',
        'gid': '0'
    }
    

    with open(GOOGLE_SHEET_RESPONSE, 'r', encoding='utf-8') as source_file:
        response_body = source_file.read()
    
    resp = responses.Response('GET', rx, body=response_body, status=200, match=[matchers.query_param_matcher(params)])

    responses.add(resp)
    
    results = gis.get_google_sheet_csv('1QwWXDMzNc7X-krErCwuzTHgXfiru-U99jJeJ6nk9hko', '0')
    assert_that(results).is_length(11)
    
    assert_that(results).contains({
        'Area':'Carrick',
        'Corner Store': 'Juba Grocery',
        'Address': '2721 Brownsville Rd',
        'City': 'Pittsburgh',
        'Zip': '15227',
        'Notes': '',
        'Participates in Food Bucks SNAP Incentive Program': ''        
    })
