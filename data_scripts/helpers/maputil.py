"""
Utilizes a JSON Schema to create a blank dictionary with default values based on data type.
"""

import calendar
from datetime import date, datetime, timedelta


def new_record(schema: dict) -> dict:
    """
    Uses a Json Schema to create an empty Record with default values based on type.

    Args:
        schema (dict): JSON Schema

    Returns:
        dict: Empty Record.
    """

    new_record = {}

    for key in schema['properties'].keys():

        prop_type = schema['properties'][key]['type']
        if type(prop_type) == list:
            new_record[key] = get_default_value(prop_type[0])
        else:
            new_record[key] = get_default_value(prop_type)
    return new_record


def get_default_value(type: str) -> str | int | bool:
    """
    Translates a given type to a Default value.

    Args:
        type (str): Data Type

    Returns:
        str|int|bool: Default Value
    """

    match type:
        case 'string':
            return ''
        case 'number':
            return 0
        case 'boolean':
            return False


def get_month_start(name: str | int) -> str | None:
    """
    Calculates the start of the current Month for a 

    Args:
        name (str|int): Month name or digit 

    Returns:
        str: Month Name with start of month
    """

    if str(name).isnumeric():
        if name >= 1 and name <= 12:
            return calendar.month_name[name] + ' 1'
    else:
        if is_month_name(name):
            return name.capitalize() + ' 1'
        elif is_month_abbr(name):
            return calendar.month_name[calendar.month_abbr.index(name.capitalize())] + ' 1'

    return None


def get_month_end(name: str | int, year: int) -> str | None:
    """
    Returns the Month End Date

    Args:
        name (str | int): Month name or digit
        year (int): Year value

    Returns:
        str: Month name and end of month digit
    """
    if str(name).isnumeric():
        if int(name) >= 1 and int(name) <= 12:
            next_month = date(year, name + 1, 1)
            end_month = next_month + timedelta(days=-1)
            return end_month.strftime('%B %-d')
    else:
        if is_month_name(name) or is_month_abbr(name):
            if is_month_name(name):
                current_month = datetime.strptime(
                    f"{name.capitalize()}/1/{year}", '%B/%d/%Y')
                next_month = date(year, current_month.month+1, 1)
            else:
                current_month = datetime.strptime(
                    f"{name.capitalize()}/1/{year}", '%b/%-d/%Y')
                next_month = date(year, current_month.month+1, 1)

            end_month = next_month + timedelta(days=-1)
            return end_month.strftime('%B %-d')
    return None


def is_month_name(value: str) -> bool:
    """
    Checks if the Value passed in is a month value.

    Args:
        value (str): String value

    Returns:
        bool: True/False
    """

    return value.capitalize() in calendar.month_name


def is_month_abbr(value: str) -> bool:
    """
    Checks if the value passed in the Month abbreviation.

    Args:
        value (str): Value to check

    Returns:
        bool: True/False
    """
    return value.capitalize() in calendar.month_abbr


def merge_location_description(record: dict, schedules: list) -> dict:
    """
    Merges the Schedules values to the Location Descriptions separated by HTML line breaks.

    Args:
        record (dict): Common Record
        schedules (list): Vendor Schedule items

    Returns:
        dict: Updated record
    """

    if schedules:
        record['location_description'] = '<br/>'.join(schedules)
    return record


def set_date_range(record: dict, schedules: list) -> dict:
    """
    Sets the date to and from on the record based on the first schedule line.

    Args:
        record (dict): Common Record
        schedules (list): List of schedules

    Returns:
        dict: Updated Record
    """

    if schedules:
        parts = str(schedules[0]).split(' ')
        # Filter out all the Non-month name values.
        months = [part for part in parts if is_month_name(
            part) or is_month_abbr(part)]

        if months:
            record['date_from'] = get_month_start(months[0])
            if len(months) > 1:
                record['date_to'] = get_month_end(
                    months[1], date.today().year)
    return record


def apply_schema(records: list, schema: dict) -> list:
    """
    Applies the Schema to the Collection of Dictionaries once read in.

    Args:
        records (list): List of dictionaries
        schema (dict): Schema 

    Returns:
        list: List of typed records
    """

    for record in records:
        apply_schema_to_record(record, schema)


def apply_schema_to_record(record: dict, schema: dict) -> None:
    """
    Applies the Schema to a given record.

    Args:
        record (dict): Dictionary
        schema (dict): Schema to apply to the Dictionary
    """

    properties = schema.get('properties', {})

    for key in properties.keys():
        if key in record:
            field_info = properties[key]
            type_info = field_info.get('type', 'string')
            if type(type_info) == list:
                record[key] = convert_value(record[key], type_info[0])
            else:
                record[key] = convert_value(record[key], type_info)


def convert_value(value: any, type: str) -> str | float | bool | int:
    """
    Converts a given value to the desired type

    Args:
        value (any): Value to convert
        type (str): Type to convert to

    Returns:
        str | float | bool: return value
    """

    match type:
        case 'string':
            return str(value)
        case 'number':
            return float(value)
        case 'boolean':
            return str(value).lower() in ('true', '1', 'yes')
        case 'integer':
            return int(value)
    return value
