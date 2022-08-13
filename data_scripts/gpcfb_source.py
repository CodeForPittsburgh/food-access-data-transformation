"""
Source Script to retrieve the Greater Pittsburgh Community Foodbank Sites
from ARC GIS API and maps to the standard output format.    
"""

import csv
import json
import logging
import os

from helpers import gis, maputil, validation
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'gpcfb-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'ARC_GIS_GPCFB_QUERY'

DELIMITER = '|'

logging.basicConfig(level=logging.INFO)


def load_schema(path: str) -> dict:
    """
    Loads the Schema file to a Dictionary.

    Args:
        path (str): Schema File path

    Returns:
        dict: Schema Dictionary
    """
    with open(path, 'r', encoding='utf-8') as input_file:
        return json.loads(input_file.read())


def write_output(records: list):
    """
    Outputs the converted records to a CSV.

    Args:
        records (list): List of Dictionaries to output
    """
    
    if not os.path.exists(RAW_OUTPUT_FOLDER):
        os.makedirs(RAW_OUTPUT_FOLDER)
    
    csv.register_dialect('output', delimiter=DELIMITER)
    with open(os.path.join(RAW_OUTPUT_FOLDER, RAW_OUTPUT_FILE), 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=records[0].keys(), dialect='output')
        writer.writeheader()
        writer.writerows(records)


def map_record(record: dict, schema: dict) -> dict:
    """
    Maps the Provided Record to the Schema

    Args:
        record (dict): GIS Attribute Listing

    Returns:
        dict: Common Model
    """

    mapped_record = maputil.new_record(schema)
    mapped_record['file_name'] = 'ARC_GIS_GPCFB_QUERY'
    mapped_record['name'] = record.get('SITE_name', '')
    mapped_record['address'] = record.get('SITE_address1', '')
    mapped_record['city'] = record.get('SITE_city', '')
    mapped_record['state'] = record.get('SITE_state', '')
    mapped_record['zip_code'] = record.get('SITE_zip', '')
    mapped_record['latitude'] = record.get('latitude', '')
    mapped_record['longitude'] = record.get('longitude', '')
    mapped_record['type'] = 'food bank site'
    mapped_record['phone'] = record.get('POC_phone', '')
    mapped_record['original_id'] = record.get('globalid', '')
    mapped_record['url'] = record.get('SITE_website', '')
    mapped_record['open_to_spec_group'] = record.get(
        'Population_Served_filter', '')
    mapped_record['source_org'] = 'Greater Pittsburgh Community Food Bank'
    mapped_record['source_file'] = 'https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer'
    mapped_record['latlng_source'] = 'Arc_GIS'

    entry = {
        'pop_serv': record.get('Population_Served', None),
        'spec_loc': record.get('SITE_specific_location', None),
        'time': record.get('Time', None),
        'pub_notes': record.get('PublicNotes', None)
    }
    mapped_record['location_description'] = join_location_description(entry)

    return RulesEngine(mapped_record).apply_global_rules().apply_food_bank_rules().commit()


def join_location_description(entries: dict) -> str | None:
    """
    Combines the list of entries into a consolidated location descriptions

    Args:
        entries (dict): listing of items to combine

    Returns:
        dict: updated common record with the location description
    """

    desc = ''

    if entries.get('pop_serv', None) and entries.get('pop_serv') != 'none_of_the_above':
        desc = desc + \
            f"Population Served: {str(entries.get('pop_serv')).strip()}<br/>"
    else:
        desc = desc + 'Population Served: Contact for more details<br/>'

    if entries.get('spec_loc', None):
        desc = desc + f"Site Info: {str(entries.get('spec_loc')).strip()}<br/>"

    if entries.get('time', None):
        desc = desc + f"Time: {str(entries.get('time')).strip()}<br/>"

    if entries.get('pub_notes', None):
        desc = desc + \
            f"Additional Info: {str(entries.get('pub_notes')).strip()}"
    return desc.replace('\n', '').replace('|', ' ')


def main():
    """
    Main Function for Processing
    """
    # Retrieve the GPCFB Sites from the ARC GIS WebServices
    logging.info(f"RETRIVING FOOD BANK SITES FROM WEB SERVICES...")
    locations = gis.get_gpcfb_sites()
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(locations)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for location in locations:
        if location.get('STATUS') == 'active':
            # Map the Record
            mapped_record = map_record(location, schema)

            # Add the Id
            mapped_record['id'] = row_number
            mapped_record['file_name'] = SOURCE
            # Validate the record
            result = validation.validate(schema, mapped_record)
            if not result.get('valid', True):
                mapped_record['in_error'] = True
                mapped_record['data_issues'] = result.get('errors', '')
                error_records = error_records + 1

            if not validation.validate_latitude(mapped_record.get('latitude', 0)) or not validation.validate_longitude(mapped_record.get('longitude', 0)):
                mapped_record['in_error'] = True
                errors = mapped_record.get('data_issues', '')
                errors = errors + '|Invalid Latitude/Longitude'
                mapped_record['data_issues'] = errors

            # Add it to the Collection
            records.append(mapped_record)
            row_number = row_number + 1
    if records:
        logging.info(
            f"OUTPUTING GPCFB FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info('DONE PROCESSING RAW GPCFB SOURCE INFORMATION')


if __name__ == '__main__':
    main()
