"""
Helper for retrieving information from the ArcGIS Web Service.
"""

import csv
import json

import requests
import logging

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

GIS_1_SERVICE = 'https://services1.arcgis.com'
GIS_5_SERVICE = 'https://services5.arcgis.com'
WIC_SERVICE = 'https://www.pawic.com'
GOOGLE_SHEETS = 'https://docs.google.com/spreadsheets/export'


def get_wic_sites() -> list:
    """
    Retrieves the listing of WIC Sites from the Web Service.

    Returns:
        list: List of Dictionaries.
    """

    resource = '/FindWICStores.aspx/FindStores'
    payload = {"county": "2", "zip": "", "miles": "5"}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.post(WIC_SERVICE + resource,
                             json=payload, headers=headers, timeout=60)

    if response.status_code == 200:
        output_json = response.json()
        if 'd' in output_json and output_json['d']:
            query_results = json.loads(output_json['d'])
            return query_results.get('Result', [])
    return []


def get_snap_sites() -> list:
    """
    Returns a list of Snap Sites from the ARC GIS Service

    Returns:
        list: List of Dictionaries
    """

    resource = '/RLQu0rK7h4kbsBq5/arcgis/rest/services/Store_Locations/FeatureServer/0/query'

    params = {
        'where': "State = 'PA' AND County = 'ALLEGHENY'",
        'outFields': '*',
        'outSR': '4326',
        'f': 'json'
    }
    results = []
    response = requests.get(GIS_1_SERVICE + resource, params=params, timeout=60)
    if response.status_code == 200:
        output = response.json()
        if 'features' in output and output['features']:
            for feature in output['features']:
                if 'attributes' in feature:
                    results.append(feature['attributes'])

    return results


def get_fmnp_markets() -> list:
    """
    Returns a listing of FMNP Sites from the ARC GIS Service.

    Returns:
        list: List of Dictionaries
    """

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

    results = []
    resource = '/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer/0/query'
    response = requests.get(GIS_5_SERVICE + resource, params=params, timeout=60)

    if response.status_code == 200:
        output = response.json()
        if 'features' in output and output['features']:
            for feature in output['features']:
                if 'attributes' in feature:
                    results.append(feature['attributes'])
    return results


def get_gpcfb_sites() -> list:
    """
    Returns a listing of Greater Pittsburgh Area Foodbank Sites.

    Returns:
        list: List of Dictionaries
    """
    results = []
    params = {
        'where': '1=1',
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

    resource = '/vdNDkVykv9vEWFX4/arcgis/rest/services/COVID19_Food_Access_(PUBLIC)/FeatureServer/0/query'

    response = requests.get(GIS_1_SERVICE + resource, params=params, timeout=60)

    if response.status_code == 200:
        output = response.json()
        if 'features' in output and output['features']:
            for feature in output['features']:
                result = feature.get('attributes', {})
                geometry = feature.get('geometry', {})
                result['longitude'] = geometry.get('x', 0)
                result['latitude'] = geometry.get('y', 0)
                results.append(result)
    return results


def get_schedule_entry(market_id: str) -> list:
    """
    Returns the Market Schedule from the Arc GIS service using the Market Id.

    Args:
        market_id (str): Market Id

    Returns:
        list: List of Dictionaries.
    """
    params = {
        'where': f"FarmMarketID='{market_id}'",
        'resultType': 'none',
        'outFields': '*',
        'sqlFormat': 'none',
        'f': 'pjson'
    }

    resource = '/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer/1/query'
    response = requests.get(GIS_5_SERVICE + resource, params=params, timeout=60)

    schedules = []
    if response.status_code == 200:
        output = response.json()
        if 'features' in output and output['features']:
            for feature in output['features']:
                schedules.append(str(feature.get('attributes').get(
                    'VendorSchedule')).strip().replace("\n", ""))
    return schedules

def get_geometry_values(record:dict) -> dict:
    """
    Retrieves the Longitude and Latitude from the geometry section.

    Args:
        record (dict): Record from the Web Services

    Returns:
        dict: Longitude/Latitude
    """
    
    geometry = record.get('geometry', {})
    coordinates = geometry.get('coordinates', [])
    if coordinates and len(coordinates) == 2:
        return {
            'longitude': coordinates[0],
            'latitude': coordinates[1]
        }
    
    return {
        'longitude': 0,
        'latitude': 0
    }

def get_summer_meal_sites() -> list:
    """
    Returns the Summer Meal Sites from the Arc GIS Service through the USDA

    Returns:
        list: List of Dictionaries
    """

    results = []
    params = {
        'outFields': '*',
        'where': "Site_State='PA' and Site_County='Allegheny'",
        'f': 'geojson'
    }
    resource = '/vdNDkVykv9vEWFX4/arcgis/rest/services/Child_Nutrition/FeatureServer/0/query'
    response = requests.get(GIS_1_SERVICE + resource, params=params, timeout=60)

    if response.status_code == 200:
        output = response.json()
        if 'features' in output and output['features']:
            for feature in output['features']:
                result = feature.get('properties', None)
                if not result.get('Latitude', None) and not result.get('Longitude', None):
                    coordinates = get_geometry_values(feature)
                    result['Longitude'] = coordinates.get('longitude', 0)
                    result['Latitude'] = coordinates.get('latitude', 0)
                results.append(feature['properties'])
    return results

def get_google_sheet_csv(sheet_id: str, gid: str) -> list:
    """
    Downloads a Google Sheet and Consumes it to a List of Dictionaries.

    Args:
        sheet_id (str): Sheet Id
        gid (str): Id Value for the tab in the sheet.

    Returns:
        list: List of Dictionaries
    """
    records = []

    params = {
        'id': sheet_id,
        'exportFormat': 'csv',
        'gid': gid
    }

    response = requests.get(GOOGLE_SHEETS, params=params, timeout=60)

    if response.status_code == 200:
        output = response.content.decode()
        lines = output.splitlines()

        csv.register_dialect('input', delimiter=',')
        reader = csv.DictReader(lines, dialect='input')
        for record in reader:
            records.append(record)
    return records
