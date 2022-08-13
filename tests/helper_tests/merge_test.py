"""
Tests for the Merge Logic    
"""

import json
import os

from assertpy import assert_that
from data_scripts.helpers import merge

FARMERS_MARKET = 'farmer\'s market'
CONVENIENCE_STORE = 'convenience store'
SUPERMARKET = 'supermarket'


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


def test_merge_record_same_source():
    """
    Test Merging logic for two records for the same source.
    """

    source = {
        'id': '334455',
        'name': 'West Side Farmer\'s Market',
        'type': FARMERS_MARKET,
        'address': '700 West St',
        'wic': True,
        'snap': False,
        'fresh_produce': True,
        'fmnp': True,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'ARC_GIS_FMNP_QUERY'
    }

    target = {
        'id': '334466',
        'name': 'Green Grocer - West Side Farmer\'s Market',
        'type': FARMERS_MARKET,
        'address': '700 West St',
        'wic': True,
        'snap': False,
        'fresh_produce': False,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'ARC_GIS_FMNP_QUERY'
    }

    records = []
    records.append(source)
    records.append(target)
    schema = load_schema()

    result = merge.merge_records(source, target, schema)
    assert_that(result)\
        .contains_entry({'name': 'Green Grocer - West Side Farmer\'s Market'})\
        .contains_entry({'wic': True})\
        .contains_entry({'snap': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'fmnp': True})


def test_merge_record_different_source():
    """
    Tests Merging logic for two records for different sources.
    """

    source = {
        'id': '334555',
        'name': 'Kuhn\'s',
        'type': SUPERMARKET, 
        'address': '700 North St',
        'wic': True,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 70,
        'source_file': 'WIC_WS_QUERY'
    }

    target = {
        'id': '3333425',
        'name': 'Green Grocer - Kuhn\'s Market',
        'type': SUPERMARKET,
        'address': '700 North St',
        'wic': False,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'ARC_GIS_SNAP_QUERY'
    }

    records = []
    records.append(source)
    records.append(target)

    schema = load_schema()
    result = merge.merge_records(source, target, schema)

    assert_that(result)\
        .contains_entry({'name': 'Green Grocer - Kuhn\'s Market'})\
        .contains_entry({'wic': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'latitude': 80})


def test_merge_record_no_heirarchy():
    """
    Tests Merging logic for two records with no heirarchy defined.
    """

    source = {
        'id': '44232455',
        'name': 'Giant Eagle',
        'type': SUPERMARKET,
        'address': '700 South St',
        'wic': True,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 70,
        'source_file': 'FART_FILE'
    }

    target = {
        'id': '117256345',
        'name': 'Green Grocer - Giant Eagle',
        'type': SUPERMARKET,
        'address': '700 South St',
        'wic': False,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'FART_FILE'
    }

    records = []
    records.append(source)
    records.append(target)

    schema = load_schema()
    result = merge.merge_records(source, target, schema)

    assert_that(result)\
        .contains_entry({'name': 'Green Grocer - Giant Eagle'})\
        .contains_entry({'wic': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'latitude': 80})


def test_deduplicate_no_duplicates():
    """
    Tests Deduplicate function with no duplicates.
    """

    source = {
        'id': '347234876234',
        'name': 'Giant Eagle Store 63',
        'type': SUPERMARKET,
        'address': '600 West St',
        'wic': True,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 70,
        'source_file': 'FART_FILE'
    }

    target = {
        'id': '2349872487',
        'name': 'Green Grocer - Giant Eagle Store 75',
        'type': SUPERMARKET,
        'address': '800 West St',
        'wic': False,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'FART_FILE'
    }

    records = []
    records.append(source)
    records.append(target)

    schema = load_schema()
    result = merge.deduplicate(records, schema)
    assert_that(result['records']).is_not_empty().is_length(2)
    assert_that(result['duplicates']).is_empty()


def test_deduplicate_other_type():
    """
    Tests Deduplicate with other type.
    """

    source = {
        'id': '123098146',
        'name': 'Giant Eagle Store 85',
        'type': SUPERMARKET,
        'address': '700 East St',
        'wic': True,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 70,
        'source_file': 'FART_FILE'
    }

    target = {
        'id': '42398746',
        'name': 'Green Grocer - Giant Eagle Store 76',
        'type': 'other',
        'address': '700 East St',
        'wic': False,
        'snap': True,
        'fresh_produce': True,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'FART_FILE'
    }

    records = []
    records.append(source)
    records.append(target)

    schema = load_schema()
    result = merge.deduplicate(records, schema)

    assert_that(result['records']).is_not_empty().is_length(2)
    assert_that(result['duplicates']).is_empty()

def test_deduplicate_merge():
    """
    Tests Mergine two records together.
    """
    
    source = {
        'id': '234876234',
        'name': 'East Side Farmer\'s Market',
        'type': FARMERS_MARKET,
        'address': '700 Main St',
        'wic': True,
        'snap': False,
        'fresh_produce': True,
        'fmnp': True,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'ARC_GIS_FMNP_QUERY'
    }

    target = {
        'id': '234987234',
        'name': 'Green Grocer - East Side Farmer\'s Market',
        'type': FARMERS_MARKET,
        'address': '700 Main St',
        'wic': True,
        'snap': False,
        'fresh_produce': False,
        'fmnp': False,
        'longitude': 90,
        'latitude': 80,
        'source_file': 'ARC_GIS_FMNP_QUERY'
    }

    records = []
    records.append(source)
    records.append(target)
    schema = load_schema()
    
    result = merge.deduplicate(records, schema)
    
    assert_that(result['records']).is_length(1)
    assert_that(result['duplicates']).is_length(2)
    
    record = result['records'][0]
    
    assert_that(record)\
        .contains_entry({'name': 'Green Grocer - East Side Farmer\'s Market'})\
        .contains_entry({'type': FARMERS_MARKET})\
        .contains_entry({'address': '700 Main St'})\
        .contains_entry({'wic': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'snap': False})\
        .contains_entry({'merged_record': True})\
        .contains_entry({'group_id': '234987234;234876234'})  
