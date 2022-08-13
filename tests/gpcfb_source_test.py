"""
GPCFB Source Tests
"""

import os
import json
from assertpy import assert_that
from data_scripts import gpcfb_source

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

def test_map_record_main_fields():
    """
    Tests the information is mapped correctly based on the rules.
    """
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Fun Site Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-1',
        'SITE_specific_location': '(none)',
        'Time': 'Mondays, Wednesdays and Fridays from 11:00 am to 2:00 pm',
        'PublicNotes': 'Grab and Go meal and snack distribution for those with silly hats.',
        'SITE_address1': '442 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': 'Available for children up to 18 years old and those with intellectual disabilities up to 21 years old.',
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_record = gpcfb_source.map_record(item, schema)
    
    assert_that(mapped_record)\
        .contains_entry({'file_name':'ARC_GIS_GPCFB_QUERY'})\
        .contains_entry({'name':'Fun Site Heights'})\
        .contains_entry({'address':'442 Mt. Pleasant Road'})\
        .contains_entry({'city':'Pittsburgh'})\
        .contains_entry({'state':'PA'})\
        .contains_entry({'zip_code':'15214'})\
        .contains_entry({'longitude': -80.0007569578037})\
        .contains_entry({'latitude': 40.478952041312951})\
        .contains_entry({'type': 'food bank site'})\
        .contains_entry({'phone': '555-555-5555'})\
        .contains_entry({'original_id':'88663be3-de50-4f31-93ed-4f6abe1323f0'})\
        .contains_entry({'url':'https://pittsburghpa.gov/citiparks/after-school-feeding-program-1'})\
        .contains_entry({'source_org':'Greater Pittsburgh Community Food Bank'})\
        .contains_entry({'source_file':'https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer'})\
        .contains_entry({'latlng_source':'Arc_GIS'})\

def test_location_description_pop_served_none():
    """
    Tests the location description calculation where the population served is none
    or None of the above
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Super Fun Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-3',
        'SITE_specific_location': None,
        'Time': None,
        'PublicNotes': None,
        'SITE_address1': '444 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': 'none_of_the_above',
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_result = gpcfb_source.map_record(item, schema)
    
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Contact for more details<br/>'})
        
    item['Population_Served'] = None
    
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Contact for more details<br/>'})
        
def test_location_description_pop_server():
    """
    Tests the location_description is mapped to the correct value from Population Served.
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Southview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-4',
        'SITE_specific_location': None,
        'Time': None,
        'PublicNotes': None,
        'SITE_address1': '445 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': 'Those with silly hats',
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_result = gpcfb_source.map_record(item, schema)
    
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Those with silly hats<br/>'})
    
def test_location_description_site_specific_address():
    """
    Tests No Site Specific Address Provided for Location Description.
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Eastview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-6',
        'SITE_specific_location': '123 Main St',
        'Time': None,
        'PublicNotes': None,
        'SITE_address1': '446 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': None,
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_result = gpcfb_source.map_record(item, schema)
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Contact for more details<br/>Site Info: 123 Main St<br/>'})
        
def test_location_description_time():
    """
    Tests the Time Field Mapping to the Location Description.
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Highview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-9',
        'SITE_specific_location': None,
        'Time': 'Mondays, Wednesdays and Fridays from 11:00 am to 1:00 pm',
        'PublicNotes': None,
        'SITE_address1': '449 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': None,
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_result = gpcfb_source.map_record(item, schema)
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Contact for more details<br/>Time: Mondays, Wednesdays and Fridays from 11:00 am to 1:00 pm<br/>'})
        
def test_location_description_public_notes_mapping():
    """
    Tests mapping the Public Notes Section to the Location Description.
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Northview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program',
        'SITE_specific_location': None,
        'Time': None,
        'PublicNotes': 'Grab and Go meal and snack distribution for children.',
        'SITE_address1': '449 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': None,
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_result = gpcfb_source.map_record(item, schema)
    assert_that(mapped_result)\
        .contains_entry({'location_description': 'Population Served: Contact for more details<br/>Additional Info: Grab and Go meal and snack distribution for children.'})
        
        
def test_location_description_full_map():
    """
    Tests all fields populated for location_description.
    """
    
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Northview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program',
        'SITE_specific_location': 'In the back',
        'Time': 'Mondays from 11:00 am to 3:00 pm',
        'PublicNotes': 'Grab and Go meal and snack distribution for some dogs.',
        'SITE_address1': '441 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': 'Available for children up to 18 years old',
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    message_test = 'Population Served: Available for children up to 18 years old<br/>Site Info: In the back<br/>Time: Mondays from 11:00 am to 3:00 pm<br/>Additional Info: Grab and Go meal and snack distribution for some dogs.'
    mapped_record = gpcfb_source.map_record(item, schema)
    assert_that(mapped_record)\
        .contains_entry({'location_description': message_test})
        
def test_fresh_produce_flag():
    """
    Tests the Fresh Produce Flag is set correctly.
    """
    schema = load_schema()
    
    item = {
        "objectid": 139,
        'globalid': '88663be3-de50-4f31-93ed-4f6abe1323f0',
        'EditDate': 1621434181549,
        'POC_name': '',
        'POC_phone': '555-555-5555',
        'POC_email': '',
        'SITE_name': 'Noview Heights',
        'SITE_website': 'https://pittsburghpa.gov/citiparks/after-school-feeding-program-10',
        'SITE_specific_location': None,
        'Time': None,
        'PublicNotes': 'Fresh groceries',
        'SITE_address1': '450 Mt. Pleasant Road',
        'SITE_address2': '',
        'SITE_city': 'Pittsburgh',
        'SITE_state': 'PA',
        'SITE_zip': '15214',
        'STATUS': 'active',
        'Population_Served': None,
        'Population_Served_filter': 'students',
        'Volunteer': 'Yes',
        'Volunteer_Info': '',
        'Limited': 'no',
        'CATEGORY': '',
        'longitude': -80.0007569578037,
        'latitude': 40.478952041312951
    }
    
    mapped_record = gpcfb_source.map_record(item, schema)
    assert_that(mapped_record)\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'free_distribution': True})
   
    