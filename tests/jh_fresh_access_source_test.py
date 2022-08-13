"""
Unit tests for Grow PGH source Mapping.
"""

import os
import json
from assertpy import assert_that

from data_scripts import jh_fresh_access_source


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


def build_item() -> dict:
    """
    Creates a record for testing.

    Returns:
        dict: Returns a mock object for testing.
    """

    return {
        'Market': 'Happy Day Market',
        'address': '100 Grant St',
        'street_one': '',
        'street two': '',
        'city': 'Pittsburgh',
        'state': 'PA',
        'zip_code': '15220',
        'Season': 'May 23rd-October 31st',
        'Date/Time': 'Thursdays 4pm-7pm',
        'weekday': 'Thursday',
        'open_time1': '4:00PM',
        'close_time1': '7:00PM',
        'description': '4th Sunday',
        'Participates in Food Bucks SNAP Incentive program': 'yes'
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
    monkeypatch.setattr(jh_fresh_access_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = build_item()

    mapped_record = jh_fresh_access_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'file_name': 'Just Harvest Google Sheets'})\
        .contains_entry({'name': 'Happy Day Market'})\
        .contains_entry({'address': '100 Grant St'})\
        .contains_entry({'city': 'Pittsburgh'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15220'})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'latitude': 40.52806})\
        .contains_entry({'longitude': -78.41051})\
        .contains_entry({'type': 'fresh access'})\
        .contains_entry({'location_description': 'May 23rd-October 31st<br/>Thursdays 4pm-7pm'})\
        .contains_entry({'snap': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'source_org': 'Just Harvest'})\
        .contains_entry({'source_file': 'Just Harvest Google Sheets'})\
        .contains_entry({'latlng_source': 'MapBox GeoCode'})


def test_map_intersection(monkeypatch):
    """
    Tests mapping for an intersection.
    """

    def mock_coordinates(record: dict) -> dict:
        """
        Returns Mock Coordinates from mapbox get_coordinates

        Returns:
            dict: Mock Result
        """
        return {
            'latitude': 50.52806,
            'longitude': -78.41051
        }

    # Mocks in the Coordinate Retrieval
    monkeypatch.setattr(jh_fresh_access_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = build_item()
    item['address'] = ''
    item['street_one'] = 'Broad St'
    item['street_two'] = 'Grant St'

    mapped_record = jh_fresh_access_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'address': 'Broad St and Grant St'})\
        .contains_entry({'latitude': 50.52806})\
        .contains_entry({'longitude': -78.41051})
