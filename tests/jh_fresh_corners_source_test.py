"""
Unit tests for Grow PGH source Mapping.
"""

import os
import json
from assertpy import assert_that

from data_scripts import jh_fresh_corners_source


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
    monkeypatch.setattr(jh_fresh_corners_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = {
        'Area': 'Carrick',
        'Corner Store': 'Juba Grocery',
        'Address': '2721 Brownsville Rd',
        'City': 'Pittsburgh',
        'Zip': '15227',
        'Notes': '',
        'Participates in Food Bucks SNAP Incentive Program': 'yes'
    }

    mapped_record = jh_fresh_corners_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'file_name': 'Just Harvest Google Sheets'})\
        .contains_entry({'name': 'Juba Grocery'})\
        .contains_entry({'address': '2721 Brownsville Rd'})\
        .contains_entry({'city': 'Pittsburgh'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15227'})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'latitude': 40.52806})\
        .contains_entry({'longitude': -78.41051})\
        .contains_entry({'type': 'convenience store'})\
        .contains_entry({'location_description': 'Carrick'})\
        .contains_entry({'snap': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'source_org': 'Just Harvest'})\
        .contains_entry({'source_file': 'Just Harvest Google Sheets'})\
        .contains_entry({'latlng_source': 'MapBox GeoCode'})


def test_map_record_no_snap(monkeypatch):
    """
    Tests mapping the record that should not have SNAP
    """

    def mock_coordinates(record: dict) -> dict:
        """
        Returns Mock Coordinates from mapbox get_coordinates

        Returns:
            dict: Mock Result
        """
        return {
            'latitude': -78.41051,
            'longitude': 40.52806
        }

    # Mocks in the Coordinate Retrieval
    monkeypatch.setattr(jh_fresh_corners_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = {
        'Area': 'Carrick',
        'Corner Store': 'Brian Grocery',
        'Address': '2724 Brownsville Rd',
        'City': 'Pittsburgh',
        'Zip': '15227',
        'Notes': '',
        'Participates in Food Bucks SNAP Incentive Program': 'no'
    }

    mapped_record = jh_fresh_corners_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'snap': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fresh_produce': True})
