"""
Unit tests for Grow PGH source Mapping.
"""

import os
import json
from assertpy import assert_that
from data_scripts import grow_pgh_source


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

def test_map_record():
    """
    Tests Mapping the CSV Record to the Common Data Model.
    """
    
    schema = load_schema()
    
    item = {
        'directory_category': 'community_garden',
        'directory_contact__email': 'smith@email.com',
        'directory_contact__fax': '555-555-5556',
        'directory_contact__mobile': '555-555-5555',
        'directory_contact__phone': '555-555-5554',
        'directory_contact__website': 'https://www.garden.com',
        'content_body': 'Im the Body',
        'directory_location__street': 'Middle Street',
        'directory_location__city':'Pittsburgh',
        'directory_location__country': 'USA',
        'directory_location__address': '123 Main St',
        'directory_location__lat': '40.440192',
        'directory_location__lng': '-80.03457',
        'directory_location__zip': '15226',
        'directory_location__state': 'PA',
        'content_post_title': 'Angora Gardens',
        'directory_social__facebook': '',
        'content_post_status': 'published',
        'field_contact_name': 'Jim Smith'
    }
    
    mapped_record = grow_pgh_source.map_record(item, schema)
    
    assert_that(mapped_record)\
        .contains_entry({'file_name':'GP_garden_directory_listing-20210322.csv'})\
        .contains_entry({'name':'Angora Gardens'})\
        .contains_entry({'address':'123 Main St'})\
        .contains_entry({'city':'Pittsburgh'})\
        .contains_entry({'state':'PA'})\
        .contains_entry({'zip_code':'15226'})\
        .contains_entry({'latitude': 40.440192})\
        .contains_entry({'longitude': -80.03457})\
        .contains_entry({'location_description':'community_garden'})\
        .contains_entry({'type':'grow pgh garden'})\
        .contains_entry({'phone':'555-555-5554'})\
        .contains_entry({'url':'https://www.garden.com'})\
        .contains_entry({'source_org':'Grow Pittsburgh'})\
        .contains_entry({'source_file':'GP_garden_directory_listing-20210322.csv'})\
        .contains_entry({'latlng_source':'Grow Pittsburgh'})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap':False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': False})\
    