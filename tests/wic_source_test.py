"""
Unit tests for WIC source Mapping.
"""

import os
import json
from assertpy import assert_that

from data_scripts import wic_source


def load_schema() -> dict:
    """
    Loads the JSON Schema

    Returns:
        dict: Dictionary of JSON Schema
    """

    schema = {}
    if os.path.exists('food-data/schema/map-data-schema.json'):
        with open('food-data/schema/map-data-schema.json', 'r', encoding='utf-8') as schema_file:
            schema = json.load(schema_file)
    return schema

def build_item():
    """
    Builds a Mock Item for Testing
    """
    
    return {
            "StoreName": "Kuhnu0027s Market Bellevue",
            "StreetAddrLine1": "661 LINCOLN AVE",
            "StreetAddrLine2": "",
            "City": "BELLEVUE",
            "State": "PA",
            "ZipCode": "15202",
            "ZipPlus4": "3405",
            "PhoneNr": "(412) 766-4546",
            "Distance": 0,
            "FormattedStreetAddr": "661 LINCOLN AVE",
            "CityStateZip": "BELLEVUE, PA 15202-3405",
            "DistanceWithText": "",
            "Directions": "http://maps.google.com?saddr=Current+Locationu0026daddr=661%20LINCOLN%20AVE%20BELLEVUE,%20PA%2015202-3405",
            "PhoneNumberWithParen": "(412) 766-4546",
            "PhoneNumberWithDash": "412-766-4546",
            "PhoneNumberLink": "tel:+1-412-766-4546"
        }

def test_map_record(monkeypatch):
    """
    Tests mapping the records from the Google Sheet
    """

    def mock_coordinates(record: dict) -> dict:
        """
        Returns Mock Coordinates from mapbox get_coordinates

        Returns:
            dict: Mock Result
        """
        return {
            'latitude': 40.52806,
            'longitude': -78.41051
        }

    # Mocks in the Coordinate Retrieval
    monkeypatch.setattr(wic_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = build_item()  

    mapped_record = wic_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'file_name': 'WIC_WS_QUERY'})\
        .contains_entry({'name': 'Kuhnu0027s Market Bellevue'})\
        .contains_entry({'address': '661 LINCOLN AVE'})\
        .contains_entry({'city': 'BELLEVUE'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15202'})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'latitude': 40.52806})\
        .contains_entry({'longitude': -78.41051})\
        .contains_entry({'type': 'supermarket'})\
        .contains_entry({'snap': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'source_org': 'PA WIC'})\
        .contains_entry({'source_file': 'https://www.pawic.com'})\
        .contains_entry({'latlng_source': 'MapBox GeoCode'})\
        .contains_entry({'url': 'http://maps.google.com?saddr=Current+Locationu0026daddr=661%20LINCOLN%20AVE%20BELLEVUE,%20PA%2015202-3405'})\
        .contains_entry({'phone': '(412) 766-4546'})
        

