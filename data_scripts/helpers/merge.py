"""
Module Logic for Merging records from a collection based on the name, type and address.
"""

from uuid import uuid4
import logging
from helpers import classification, maputil, validation
from helpers.rules import RulesEngine

logging.basicConfig(level=logging.INFO)

SOURCE_HIERARCHY = {
    'GP_garden_directory_listing-20210322.csv': {
        'coordinates': 2,
        'fresh_produce': 2
    },
    'ARC_GIS_SNAP_QUERY': {
        'coordinates': 1,
        'snap': 1,
        'fresh_produce': 3
    },
    'WIC_WS_QUERY': {
        'coordinates': 2,
        'wic': 1
    },
    'ARC_GIS_SUMMER_MEAL_QUERY': {
        'coordinates': 1,
        'free_distribution': 1
    },
    'ARC_GIS_FMNP_QUERY': {
        'coordinates': 1,
        'wic': 2,
        'fmnp': 1,
        'fresh_produce': 1
    },
    'ARC_GIS_GPCFB_QUERY': {
        'coordinates': 1,
        'free_distribution': 1
    },
    'Just Harvest Google Sheets': {
        'coordinates': 2,
        'snap': 2,
        'food_bucks': 1,
        'free_distribution': 1,
        'fresh_produce': 2
    }
}


def deduplicate(records: list, schema: dict) -> dict:
    """
    De-deuplicates a list of dictionaries based on the Address, type and name. 
    Returns a dictionary containing the deduplicated list and the duplicate records removed.

    Args:
        records (list): Initial listing of records to de-duplicate
        schema (dict): JSON Schema

    Returns:
        dict: Dictionary containing the de-duplicated list and duplicate record removed.
    """
    address_map = {}
    recs = []
    dupes = []

    for record in records:
        maputil.apply_schema_to_record(record, schema)
        if record['address'] not in address_map:
            address_map[str(record['address'])] = []
        address_map[record['address']].append(record)

    for address in address_map.keys():
        address_set = address_map[address]
        if len(address_set) > 1:
            # Dedupe the set
            result = process_duplicates(address_set, schema)
            recs.extend(result['records'])
            dupes.extend(result['duplicates'])
        else:
            # Add the set collection to the records list
            recs.append(min(address_set))

    return {
        'records': recs,
        'duplicates': dupes
    }


def process_duplicates(addresses: list, schema: dict) -> dict:
    """
    Processes a given set and returns a dictionary of items which containing the 
    duplicates and de-duped records

    Args:
        addresses (list): address set

    Returns:
        dict: Dictionary of results
    """

    records = []
    dupes = []
    while len(addresses) > 0:
        if len(addresses) >= 2:
            item1 = addresses.pop()
            item2 = addresses.pop()

            if item1['type'] == item2['type'] and classification.get_reg_ex(item1['name'], item1['type']) == classification.get_reg_ex(item2['name'], item2['type']):
                result = merge_records(item1, item2, schema)
                records.append(result)
                dupes.append(item1)
                dupes.append(item2)
            
                if len(addresses) % 2 > 0:
                    addresses.append(result)
            
            else:
                records.append(item1)
                records.append(item2)
        else:
            records.append(addresses.pop())
        
    return {
        'records': records,
        'duplicates': dupes
    }


def merge_records(source: dict, target: dict, schema: dict) -> dict:
    """
    Merges two records based on name, type and address.
    The main focus for the merge is the name and the Flags

    Args:
        source (dict): First Record to compare
        target (dict): Second Record to compare.
        schema (dict): JSON Schema

    Returns:
        dict: Result with the Record and the Duplicate
    """
    skip_fields = ['wic', 'fmnp', 'food_bucks', 'snap',
                   'longitude', 'latitude', 'fresh_produce', 'free_distribution', 'id', 'in_error']

    record = maputil.new_record(schema)
    for key in source.keys():
        if key not in skip_fields:
            record[key] = merge_value(source, target, key)

    coordinates = get_coordinates(source, target)
    record['longitude'] = coordinates['longitude']
    record['latitude'] = coordinates['latitude']

    record['wic'] = bool(get_flag_value(source, target, 'wic'))
    record['snap'] = bool(get_flag_value(source, target, 'snap'))
    record['food_bucks'] = bool(get_flag_value(source, target, 'food_bucks'))
    record['fmnp'] = bool(get_flag_value(source, target, 'fmnp'))
    record['free_distribution'] = bool(get_flag_value(
        source, target, 'free_distribution'))
    record['fresh_produce'] = bool(get_flag_value(source, target, 'fresh_produce'))
    record['merged_record'] = True
    record['group_id'] = f"{source['id']};{target['id']}"
    record['original_id'] = str(uuid4())
    record['id'] = 0

    validation_result = validation.validate(schema, record)
    if validation_result['valid'] is True:
        record['in_error'] = False
        return RulesEngine(record).apply_global_rules().commit()
    else:
        record['in_error'] = True
        record['data_issues'] = validation_result.get('errors', '')
        return RulesEngine(record).apply_global_rules().commit()


def merge_value(source: dict, target: dict, field:str) -> int|float|str|bool:
    """
    Merges values of each field based on if the value is equal or is longer.

    Args:
        source (dict): source record
        target (dict): target record
        field (string): field to merge
        schema (dict): Json schema

    Returns:
        value
    """

    if source[field] != target[field] and len(target[field]) > len(source[field]):
        return target[field]
    else:
        return source[field]


def get_flag_value(source: dict, target: dict, field: str) -> bool:
    """
    Returns the flag Value for two records that need merged

    Args:
        source (dict): Source Record
        target (dict): Target Record
        field (str): Field name to check

    Returns:
        bool: flag Value
    """

    if source['source_file'] != target['source_file']:
        if SOURCE_HIERARCHY.get(source['source_file'], {}).get(field, 100) < SOURCE_HIERARCHY.get(target['source_file'], {}).get(field, 100):
            return source.get(field, False)
        elif SOURCE_HIERARCHY.get(source['source_file'], {}).get(field, 100) > SOURCE_HIERARCHY.get(target['source_file'], {}).get(field, 100):
            return target.get(field, False)
    return source.get(field, False) is True or target.get(field, False) is True


def get_coordinates(source: dict, target: dict) -> dict:
    """
    Returns the Coordinates for the merged record

    Args:
        source (dict): Source Record
        target (dict): Target Record

    Returns:
        dict: Longitude and Latitude
    """

    if source['source_file'] != target['source_file'] and source['longitude'] != target['longitude'] and source['latitude'] != target['latitude']:
        if SOURCE_HIERARCHY.get(source['source_file'], {}).get('coordinates', 100) < SOURCE_HIERARCHY.get(target['source_file'], {}).get('coordinates', 100) and source['longitude'] != 0 and source['latitude'] != 0:
            return {
                'longitude': source['longitude'],
                'latitude': source['latitude']
            }

    if (target['longitude'] != 0 and target['latitude'] != 0):
        return {
            'longitude': float(target['longitude']),
            'latitude': float(target['latitude'])
        }

    else:
        return {
            'longitude': float(source['longitude']),
            'latitude': float(source['latitude'])
        }
