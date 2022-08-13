"""
Unit tests for Grow PGH source Mapping.
"""

import os
import json
from assertpy import assert_that

from data_scripts import jh_bridgeway_capital_source

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
    return {
        'Neighborhood': 'Arnold',
        'Store Name': 'Veggie House',
        'Address': '310 17th St',
        'City': 'Pittsburgh',
        'State': 'PA',
        'Zip': '15227',
        'Tag': 'Fresh produce available',
        'Notes': 'Urban Farm'  
    }

def test_map_record(monkeypatch):
    """
    Tests mapping the records from the Google Sheet
    """
    
    def mock_coordinates(record:dict) -> dict:
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
    monkeypatch.setattr(jh_bridgeway_capital_source,'get_coordinates', mock_coordinates)
    
    schema = load_schema()
    item = build_item()
    
    mapped_record = jh_bridgeway_capital_source.map_record(item, schema)
    
    assert_that(mapped_record)\
        .contains_entry({'file_name':'Just Harvest Google Sheets'})\
        .contains_entry({'name':'Veggie House'})\
        .contains_entry({'address':'310 17th St'})\
        .contains_entry({'city':'Pittsburgh'})\
        .contains_entry({'state':'PA'})\
        .contains_entry({'zip_code':'15227'})\
        .contains_entry({'county':'Allegheny'})\
        .contains_entry({'latitude': 40.52806})\
        .contains_entry({'longitude':-78.41051})\
        .contains_entry({'type':'other'})\
        .contains_entry({'location_description':'Arnold<br />Fresh produce available<br />Urban Farm'})\
        .contains_entry({'snap':False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'source_org':'Just Harvest'})\
        .contains_entry({'source_file':'Just Harvest Google Sheets'})\
        .contains_entry({'latlng_source':'MapBox GeoCode'})
    
def test_notes_to_type(monkeypatch):
    """
    Tests that Corner Store is mapped to Convenience store.
    """
    
    def mock_coordinates(record:dict) -> dict:
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
    monkeypatch.setattr(jh_bridgeway_capital_source,'get_coordinates', mock_coordinates)
    
    schema = load_schema()
    item = build_item()    
    item['Notes'] = 'corner store'    
    
    mapped_record = jh_bridgeway_capital_source.map_record(item, schema)
    assert_that(mapped_record).is_not_none().contains_entry({'type': 'convenience store'})
    

def test_exlusion_filter(monkeypatch):
    """
    Tests the exclusion of items that are not tagged as 
    health food available or fresh produce available
    """
    
    def mock_coordinates(record:dict) -> dict:
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
    monkeypatch.setattr(jh_bridgeway_capital_source,'get_coordinates', mock_coordinates)
    
    schema = load_schema()
    item = build_item()
    item['Tag'] = 'SNAP'
    
    mapped_record = jh_bridgeway_capital_source.map_record(item, schema)
    
    assert_that(mapped_record).is_none()
    
    