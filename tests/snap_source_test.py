"""
Tests for the SNAP Source Script    
"""

from data_scripts import snap_source
from assertpy import assert_that

import json
import os

FARMER_MARKET = "farmer's market"
CONVENIENCE_STORE = 'convenience store'
FOOD_BANK_SITE = 'food bank site'
SUPERMARKET = 'supermarket'
OTHER = 'other'

def load_schema() -> dict:
    """
    Loads the JSON Schema

    Returns:
        dict: JSON Schema
    """
    
    schema = {}
    if os.path.exists('food-data/schema/map-data-schema.json'):
        with open('food-data/schema/map-data-schema.json', 'r', encoding='utf-8') as schema_file:
            schema = json.load(schema_file)
    return schema
    
def build_item(name: str) -> dict:
    """
    Builds a Mock items for testing

    Returns:
        dict: Mock Item
    """
    return {
        "Store_Name": name,
        "Address": "1 N Linden St",
        "Address_Line__2": None,
        "City": "Duquesne",
        "State": "PA",
        "Zip5": "15110",
        "Zip4": "1097",
        "County": "ALLEGHENY",
        "Longitude": -79.8433,
        "Latitude": 40.375511,
        "ObjectId": 116022
    }

def test_map_record_food_bank():
    """
    Tests Mapping SNAP Food Bank Records
    """
    
    record = build_item('Green Grocer - Greater Pittsburgh Comm Food Bank')
    schema = load_schema()
    result = snap_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'name': "Green Grocer - Greater Pittsburgh Comm Food Bank"})\
        .contains_entry({'address': '1 N Linden St'})\
        .contains_entry({'city': 'Duquesne'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15110'})\
        .contains_entry({'latitude': 40.375511})\
        .contains_entry({'longitude': -79.8433})\
        .contains_entry({'county': 'ALLEGHENY'})\
        .contains_entry({'original_id': '116022'})\
        .contains_entry({'source_org': 'USDA Food and Nutrition Service'})\
        .contains_entry({'source_file': 'https://services1.arcgis.com/RLQu0rK7h4kbsBq5/arcgis/rest/services/Store_Locations/FeatureServer'})\
        .contains_entry({'latlng_source': 'Arc_Gis'})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': True})\
        .contains_entry({'type': FOOD_BANK_SITE})\
        .contains_entry({'file_name': 'ARC_GIS_SNAP_QUERY'})

def test_map_record_convenience_store():
    """
    Tests Mapping a record that is a convenience store.
    """
    
    record = build_item('Get-Go')
    schema = load_schema()
    result = snap_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'fresh_produce': False})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': CONVENIENCE_STORE})

def test_map_record_supermarket():
    """
    Test mapping a record that is a supermarket
    """
    record = build_item('Kuhn\'s Market')
    schema = load_schema()
    result = snap_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': SUPERMARKET})
        
def test_map_record_farmers_market():
    """
    Test Mapping a Farmers Marker Record
    """
    
    record = build_item('Beachview Farmer\'s Market')
    schema = load_schema()
    result = snap_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': FARMER_MARKET})
        
def test_map_record_other():
    """
    Test Mapping a Record that should be Other.
    """
    record = build_item('Donut Connection')
    schema = load_schema()
    result = snap_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'fresh_produce': False})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': OTHER})