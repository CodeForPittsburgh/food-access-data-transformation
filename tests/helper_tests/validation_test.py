"""
Unit tests for the validation helper.
"""

from assertpy import assert_that
from data_scripts.helpers import validation


def get_schema():

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "http://codeforpittsburgh.github.io/food-data-map-data",
        "name": "food-map-data-schema",
        "description": "Data Schema for records to be used in the Food Data Map.",
        "type": "object",
        "properties": {
            "id": {
                "description": "Integer row number",
                "type": "number"
            },
            "name": {
                "description": "Name of the thingy",
                "type": "string"
            }

        }
    }


def test_validation():
    """
    Tests a successful Validation.
    """

    schema = get_schema()
    schema['required'] = ["id", "name"]

    record = {
        "id": 12345,
        "name": "My Records"
    }

    result = validation.validate(schema, record)
    assert_that(result, 'Result should be valid').is_not_none(
    ).contains_entry({"valid": True})


def test_validation_missing_required_field():
    """
    Tests a failed validation with a missing field.
    """

    schema = get_schema()
    schema['required'] = ["id", "name"]
    record = {
        "id": 12345
    }

    result = validation.validate(schema, record)
    assert_that(result, 'Result should be invalid due to missing field').is_not_none(
    ).contains_entry({"valid": False})


def test_validation_wrong_data_type():
    """
    Tests a failed validation with an incorrect datatype
    """

    schema = get_schema()
    schema['required'] = ["id", "name"]
    record = {
        "id": 12345,
        "name": 123456789
    }

    result = validation.validate(schema, record)
    assert_that(result, 'Result should be invalid due to invalid datatype').is_not_none(
    ).contains_entry({"valid": False})\
        .contains_entry({"errors": "$.name is invalid: 123456789 is not of type 'string'"})


def test_validation_missing_nonrequired_field():
    """
    Tests a Validation for a missing non-required field.
    """

    schema = get_schema()
    schema['required'] = ["id"]
    record = {
        "id": 12345
    }

    result = validation.validate(schema, record)
    assert_that(result, 'Result should be valid').is_not_none(
    ).contains_entry({"valid": True})


def test_validate_longitude():
    """
    Tests validation that Longitude value is between -82 and -78
    """
    
    assert_that(validation.validate_longitude(-80)).is_true()
    
def test_validate_longitude_equal_range():
    """
    Tests when the Longitude value is equal to the range.
    """
    
    assert_that(validation.validate_longitude(-82)).is_true()
    assert_that(validation.validate_longitude(-78)).is_true()
    
def test_validate_invalid_longitude():
    """
    Tests validation that the Longitude provide is not between -82 and -78
    """
    assert_that(validation.validate_longitude(-99)).is_false()
    
    
def test_validate_latitude():
    """
    Tests validation that the Latitude is between 39 and 42
    """

    assert_that(validation.validate_latitude(40)).is_true()
    
def test_validate_latitude_equal_range():
    """
    Test when the latitude is equal to the range.
    """
    
    assert_that(validation.validate_latitude(39)).is_true()
    assert_that(validation.validate_latitude(42)).is_true()
    
def test_validate_invalid_latitude():
    """
    Tests validation that the latitude provide it not between 39 and 42
    """
    
    assert_that(validation.validate_latitude(25)).is_false()
    
def test_validate_zero_latitude():
    """
    Tests that a latitude of 0 is invalid.
    """
    
    assert_that(validation.validate_latitude(0)).is_false()
    
def test_validate_zero_longitude():
    """
    Tests that a longitude of 0 is invalid.
    """
    
    assert_that(validation.validate_longitude(0)).is_false()