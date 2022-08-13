"""
Helper that leverages JSON Schema to validate Records
"""

import jsonschema
from jsonschema.exceptions import ValidationError


def validate(schema: dict, record: dict) -> dict:
    """
    Validates a provided record against a JSON Schema.

    Args:
        schema_path (dict): JSON Schema
        record (dict): Record to validate

    Returns:
        dict: Object containing Valid/Invalid with 
        Error Messages.
    """

    try:
        jsonschema.validate(record, schema)
        return {
            'valid': True,
            'errors': ''
        }
    except ValidationError as e:
        return {
            'valid': False,
            'errors': f"{e.json_path} is invalid: {e.message}"
        }


def validate_longitude(longitude: float) -> bool:
    """
    Validates if the Longitude is within the defined range.

    Args:
        longitude (int): longitude value.

    Returns:
        bool: True/False
    """

    return -82 <= longitude <= -78


def validate_latitude(latitude: float) -> bool:
    """
    Validates that the Latitude is within the defined range.

    Args:
        latitude (int): Latitude value

    Returns:
        bool: True/False
    """

    return 39 <= latitude <= 42
