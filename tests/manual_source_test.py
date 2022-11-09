"""
Unit tests for Grow PGH source Mapping.
"""

import os
import json
from assertpy import assert_that

from data_scripts import manual_source


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
        'name': 'Best Food Market',
        'type': 'supermarket',
        'address':'123 Main St',
        'city': 'Pittsburgh',
        'state': 'PA',
        'zip_code': '15323',
        'county': 'Allegheny',
        'location_description': 'May 23rd-October 31st\nThursdays 4pm-7pm',
        'phone': '555-555-5555',
        'url': 'www.google.com',
        'date_from': '1/22/2022',
        'date_to': '5/30/2022',
        'open_to_spec_group': '',
        'food_rx': True,
        'food_bucks': False,
        'snap': True,
        'wic': True,
        'fmnp': False,
        'fresh_produce': True,
        'free_distribution': False
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
    monkeypatch.setattr(manual_source,
                        'get_coordinates', mock_coordinates)

    schema = load_schema()
    item = build_item()

    mapped_record = manual_source.map_record(item, schema)

    assert_that(mapped_record)\
        .contains_entry({'file_name': 'Manual Sources Google Sheets'})\
        .contains_entry({'name': 'Best Food Market'})\
        .contains_entry({'address': '123 Main St'})\
        .contains_entry({'city': 'Pittsburgh'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15323'})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'latitude': 40.52806})\
        .contains_entry({'longitude': -78.41051})\
        .contains_entry({'type': 'supermarket'})\
        .contains_entry({'location_description': 'May 23rd-October 31st<br/>Thursdays 4pm-7pm'})\
        .contains_entry({'snap': True})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'food_rx': True})\
        .contains_entry({'date_from': '1/22/2022'})\
        .contains_entry({'date_to': '5/30/2022'})\
        .contains_entry({'source_org': 'PFPC'})\
        .contains_entry({'source_file': 'Manual Sources Google Sheets'})\
        .contains_entry({'latlng_source': 'MapBox GeoCode'})
