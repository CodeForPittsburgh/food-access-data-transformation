"""
Tests for the Summer Meal Source Script
"""

from data_scripts import summer_meal_source
from assertpy import assert_that

import json
import os

SUMMER_MEAL = 'summer meal site'

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
        "OBJECTID": 64,
        "Site_ID_External": 177429,
        "Site_ID_External_Source": 71467,
        "Sponsor_Name": "Mt Lebanon School District",
        "Site_Name": name,
        "Site_Street": "155 Cochran Rd",
        "Site_Street2": "C20 Entrance",
        "Site_City": "Pittbusrgh",
        "Site_State": "PA",
        "Site_County": "Allegheny",
        "Latitude": 40.37571211,
        "Longitude": -80.05151279,
        "Service_Type": "Grab and Go",
        "Site_Hours": "Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.",
        "Site_Closed_Checkbox": 0,
        "General_Public_URL": "",
        "Child_Nutrition_Sponsor_ID": "a481I000000ZDMa",
        "Child_Nutrition_Site_ID": "a491I000000VOVm",
        "Site_ID_Long": "a491I000000VOVmQAO",
        "Comments": "Please contact the site to confirm the information.",
        "Sponsor_Instructions": "",
        "Site_Instructions": "The weekly menu can be found here: https://www.mtlsd.org/district/food-service",
        "Site_Zip": "15228",
        "Start_Date": 1623038400000,
        "End_Date": 1630296000000
    }

def test_map_record_summer_site():
    """
    Tests Mapping SNAP Food Bank Records
    """
        
    record = build_item('Mt. Lebanon SHS')
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'name': 'Mt. Lebanon SHS'})\
        .contains_entry({'address': '155 Cochran Rd'})\
        .contains_entry({'city': 'Pittbusrgh'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15228'})\
        .contains_entry({'latitude': 40.37571211})\
        .contains_entry({'longitude':-80.05151279})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'original_id': '177429'})\
        .contains_entry({'source_org': 'Allegheny County'})\
        .contains_entry({'source_file': 'https://services1.arcgis.com/vdNDkVykv9vEWFX4/arcgis/rest/services/Child_Nutrition/FeatureServer'})\
        .contains_entry({'date_from': 'June 07, 2021'})\
        .contains_entry({'date_to': 'August 30, 2021'})\
        .contains_entry({'latlng_source': 'Arc_Gis'})\
        .contains_entry({'fresh_produce': False})\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': True})\
        .contains_entry({'type': SUMMER_MEAL})\
        .contains_entry({'file_name': 'ARC_GIS_SUMMER_MEAL_QUERY'})\
        .contains_entry({'open_to_spec_group': 'children and teens 18 and younger'})\
        .contains_entry({'location_description': 'Site Location Info: C20 Entrance<br/>Service Type: Grab and Go<br/>Site Hours: Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.<br/>Comments: Please contact the site to confirm the information.<br/>Site Instructions: The weekly menu can be found here: https://www.mtlsd.org/district/food-service'})

def test_map_location_description_no_street2():
    """
    Tests Mapping the location_description without a Street 2 field.
    """
    
    desc = 'Service Type: Grab and Go<br/>'\
        'Site Hours: Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.<br/>'\
        'Comments: Please contact the site to confirm the information.<br/>'\
        'Site Instructions: The weekly menu can be found here: https://www.mtlsd.org/district/food-service'

    record = build_item('Mt. Lebanon JHS')
    record['Site_Street2'] = None
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    
    assert_that(result)\
        .contains_entry({'location_description': desc})
 
def test_map_location_description_no_service_type():
    """
    Tests Mapping the location_descrition without a Service_Type
    """
     
    desc = 'Site Location Info: C20 Entrance<br/>'\
        'Site Hours: Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.<br/>'\
        'Comments: Please contact the site to confirm the information.<br/>'\
        'Site Instructions: The weekly menu can be found here: https://www.mtlsd.org/district/food-service'
        
    record = build_item('Mt. Lebanon HS')
    record['Service_Type'] = None
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    assert_that(result).contains_entry({'location_description': desc})
    
def test_map_location_description_no_site_hours():
    """
    Tests Mapping the location_description without a Service_Type
    """
    
    desc = 'Site Location Info: C20 Entrance<br/>'\
        'Service Type: Grab and Go<br/>'\
        'Comments: Please contact the site to confirm the information.<br/>'\
        'Site Instructions: The weekly menu can be found here: https://www.mtlsd.org/district/food-service'
        
    record = build_item('Mt. Lebanon MS')
    record['Site_Hours'] = None
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    assert_that(result).contains_entry({'location_description': desc})
        
def test_map_location_description_no_comments():
    """
    Tests mapping the location_description wihtout the comments field.
    """
    
    desc = 'Site Location Info: C20 Entrance<br/>'\
        'Service Type: Grab and Go<br/>'\
        'Site Hours: Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.<br/>'\
        'Site Instructions: The weekly menu can be found here: https://www.mtlsd.org/district/food-service'
        
    record = build_item('Mt. Lebanon MS1')
    record['Comments'] = None
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    assert_that(result).contains_entry({'location_description': desc})
    
def test_map_location_description_no_site_instructions():
    """
    Tests mapping the location_description without a Comments field.
    """
    
    desc = 'Site Location Info: C20 Entrance<br/>'\
        'Service Type: Grab and Go<br/>'\
        'Site Hours: Monday through Friday this site provides breakfast and lunch for every child from 10:45 AM to 1:15 PM.<br/>'\
        'Comments: Please contact the site to confirm the information.<br/>'\
    
    record = build_item('Mt. Lebanon MS2')
    record['Site_Instructions'] = None
    schema = load_schema()
    result = summer_meal_source.map_record(record, schema)
    assert_that(result).contains_entry({'location_description': desc})
        