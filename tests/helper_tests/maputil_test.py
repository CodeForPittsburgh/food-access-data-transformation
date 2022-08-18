"""
Tests for creating an empty record from a Json Schema File.    
"""

from data_scripts.helpers import maputil
from assertpy import assert_that

FARMER_MARKET = "farmer's market"

def get_schema():

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://codeforpittsburgh.github.io/food-data-map-data",
        "name": "food-map-data-schema",
        "description": "Data Schema for records to be used in the Food Data Map.",
        "type": "object",
        "properties": {


        }
    }


def test_create_record_default_strings():
    """
    Tests creating a record from a schema with default strings.
    """

    schema = get_schema()

    schema['properties']['name'] = {
        "description": "Name of the record",
        "type": "string"
    }

    result = maputil.new_record(schema)

    assert_that(result, 'Result should have a field for name and it should be empty').is_equal_to(
        {'name': ''})

def test_create_record_default_strings_multiple():
    """
    Tests creating a record for properties that except null and strings.
    """
    schema = get_schema()

    schema['properties']['name'] = {
        "description": "Name of the record",
        "type": ["string", 'null']
    }

    result = maputil.new_record(schema)

    assert_that(result, 'Result should have a field for name and it should be empty').is_equal_to(
        {'name': ''})
    
def test_create_record_default_numbers():
    """
    Tests creating a record from a schema with default numbers
    """

    schema = get_schema()
    schema['properties']['id'] = {
        "description": "Integer row number",
        "type": "number"
    }
    result = maputil.new_record(schema)
    assert_that(
        result, 'Result should have a field for id and it should be 0').is_equal_to({'id': 0})


def test_create_record_default_boolean():
    """
    Tests creating a record from a schema with default booleans
    """

    schema = get_schema()
    schema['properties']['is_active'] = {
        "description:": "Denotes the record is active",
        "type": "boolean"
    }
    result = maputil.new_record(schema)

    assert_that(result, 'Result should have a field named is_active and should be false').is_equal_to(
        {'is_active': False})


def test_create_record_schema_no_properties():
    """
    Tests creating a record from a schema with no properties.
    """
    schema = get_schema()
    result = maputil.new_record(schema)
    assert_that(result, 'Result should be empty').is_empty()


def test_create_record_multiple_fields():
    """
    Tests multiple fields are added.
    """

    schema = get_schema()
    schema['properties']['id'] = {
        "description": "Integer row number",
        "type": "number"
    }
    schema['properties']['name'] = {
        "description": "Name of the thingy",
        "type": "string"
    }
    schema['properties']["is_active"] = {
        "description:": "Denotes the record is active",
        "type": "boolean"
    }
    result = maputil.new_record(schema)
    assert_that(
        result, 'Id Field should be present with a value of 0').contains_entry({'id': 0})
    assert_that(result, 'Name field should be present with a value of empty string').contains_entry(
        {'name': ''})
    assert_that(result, 'is_active field should be present with a value of false').contains_entry(
        {'is_active': False})

def test_get_month_start_name():
    """
    Tests Returning the Month name and the start digit from the name passed in.
    """
    
    result = maputil.get_month_start('April')
    assert_that(result).is_equal_to('April 1')
    
def test_get_month_start_digit():
    """
    Tests returning the Month name and start digit from passing in the digit.
    """
    
    result = maputil.get_month_start(7)
    assert_that(result).is_equal_to('July 1')
    
def test_get_month_start_invalid_month():
    """
    Tests that None is returned if an invalid month name is sent.
    """
    
    result = maputil.get_month_start('fart')
    assert_that(result).is_none()
    
def test_get_month_start_invalid_month_digit():
    """
    Tests that None is returns if an invalid month number is sent
    """
    
    result = maputil.get_month_start(16)
    assert_that(result).is_none()

def test_get_month_end_name():
    """
    Tests returning the Month name and end digit from the name passed in.
    """
    
    result = maputil.get_month_end('july', 2022)
    assert_that(result, 'Should return July 31').is_equal_to('July 31')
    
def test_get_month_end_digit():
    """
    Tests returning the Month name and end digit from the digit passed in.
    """
    
    result = maputil.get_month_end(7, 2022)
    assert_that(result, 'Result should be July 31').is_equal_to('July 31')
    
def test_get_month_end_invalid_month_name():
    """
    Test None is returned if an invalid month name is passed.
    """
    
    result =maputil.get_month_end('farts', 2022)
    assert_that(result).is_none()
    
def test_get_month_end_invalid_digit():
    """
    Tests None is returned if an invalid month digit is passed.
    """
    
    result = maputil.get_month_end(14, 2002)
    assert_that(result).is_none()
    
def test_is_month():
    """
    Test True is returned for an accurate month name.
    """
    
    result = maputil.is_month_name('October')
    assert_that(result).is_true()
    
def test_is_month_invalid():
    """
    Tests False is returned for inaccurate month name.
    """
    
    result = maputil.is_month_name('fart')
    assert_that(result).is_false()

def test_is_month_abbr():
    """
    Tests True is returned for an accurate Month Abbreviation
    """
    
    result = maputil.is_month_abbr('Oct')
    assert_that(result).is_true()
    
def test_is_month_abbr_invalid_month():
    """
    Tests False is returned for an inacturate month.
    """
    
    result = maputil.is_month_abbr('fart')
    assert_that(result).is_false()
    
def test_merge_schedule():
    """
    Tests merging the schedule to the standard record in the location_description field.
    """
    
    mapped_record = {
        'name': 'Bradly Farmer Market',
        'type': FARMER_MARKET,
        'fresh_produce': True,
        'original_id': 21,
        'snap': True 
    }
    
    schedules = ['Tuesdays', 'Wednesdays', 'Thursdays']
    
    result = maputil.merge_location_description(mapped_record, schedules)
    
    assert_that(result, 'Should have the items merged with HTML Breaks').contains_entry({'location_description': 'Tuesdays<br/>Wednesdays<br/>Thursdays'})
    
    
def test_merge_schedule_no_entries():
    """
    Tests merging the schedule to the standard record when there are not entries.
    """
    
    mapped_record = {
        'name': 'Johnson Farmer Market',
        'type': FARMER_MARKET,
        'fresh_produce': True,
        'original_id': 21,
        'location_description': '',
        'snap': True,        
        'date_from': '',
        'date_to': ''
    }
    
    schedules = []
    
    result = maputil.merge_location_description(mapped_record, schedules)
    assert_that(result, 'location_description should be empty')\
        .contains_entry({'location_description': ''})\

def test_set_date_range():
    """
    Testsing adding the vendor schedule to the location_description and setting the to and from dates.
    """
    
    mapped_record = {
        'name': 'Johnson Farmer Market',
        'type': FARMER_MARKET,
        'fresh_produce': True,
        'original_id': 21,
        'snap': True,        
        'date_from': '',
        'date_to': ''
    }
    
    schedules = ['July - October Tuesday - Sunday 12:00 PM - 5:30 PM']
    
    result = maputil.set_date_range(mapped_record, schedules)
    assert_that(result, 'location_dscription, date_from and date_to should be set')\
        .contains_entry({'date_from': 'July 1'})\
        .contains_entry({'date_to': 'October 31'})

def test_date_range_single_entry():
    """
    Tests that only the Start is set when only one month is set.
    """
    
    mapped_record = {
        'name': 'Mayview Farmer Market',
        'type': FARMER_MARKET,
        'fresh_produce': True,
        'original_id': 21,
        'snap': True,
        'date_from': '',
        'date_to': ''
    }
    
    schedules = ['March Tuesday - Sunday 12:00 PM - 5:30 PM']
    
    result = maputil.set_date_range(mapped_record, schedules)
    assert_that(result, 'date_from and date_to should be set')\
        .contains_entry({'date_from': 'March 1'})\
        .contains_entry({'date_to': ''})

def test_apply_schema_to_record():
    """
    Tests applying type information to a dictionary from a schema
    """
    
    schema = get_schema()
    schema['properties']['id'] = {
        "description": "Integer row number",
        "type": "number"
    }
    schema['properties']['name'] = {
        "description": "Name of the thingy",
        "type": "string"
    }
    schema['properties']['type'] = {
        "description": "Type of the record",
        "type": ["string", 'null']
    }
    schema['properties']['is_active'] = {
        "description:": "Denotes the record is active",
        "type": "boolean"
    }
    schema['properties']['in_error'] = {
        "description": "Denotes the recvord is in error",
        "type": "boolean"
    }
    
    record = {
        'id': '1234',
        'name': 'My Name',
        'type': 'goofy',
        'is_active': 'False',
        'in_error': 'True'
        
    }
    
    maputil.apply_schema_to_record(record, schema)
    
    assert_that(record['id']).is_type_of(float).is_equal_to(1234)
    assert_that(record['name']).is_type_of(str).is_equal_to('My Name')
    assert_that(record['type']).is_type_of(str).is_equal_to('goofy')
    assert_that(record['is_active']).is_type_of(bool).is_false()
    assert_that(record['in_error']).is_type_of(bool).is_true()
    
    
    