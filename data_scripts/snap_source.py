"""
Retrieves the Information for SNAP locations 
from the ARC GIS Web Services.
"""

import csv
import json
import logging
import os

from helpers import gis, maputil, validation, classification
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'snap-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'ARC_GIS_SNAP_QUERY'

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
        records (list): List of Dictionaries to output.
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
        record (dict): GIS Record

    Returns:
        dict: Mapped Record
    """

    mapped_record = maputil.new_record(schema)
    mapped_record['name'] = record.get('Store_Name', '')
    mapped_record['address'] = record.get('Address', '')
    mapped_record['city'] = record.get('City', '')
    mapped_record['state'] = record.get('State', '')
    mapped_record['zip_code'] = record.get('Zip5', '')
    mapped_record['latitude'] = record.get('Latitude', 0)
    mapped_record['longitude'] = record.get('Longitude', 0)
    mapped_record['type'] = classification.find_type(record.get('Store_Name', ''))
    mapped_record['county'] = record.get('County', '')
    mapped_record['original_id'] = str(record.get('ObjectId', ''))
    mapped_record['source_org'] = 'USDA Food and Nutrition Service'
    mapped_record['source_file'] = 'https://services1.arcgis.com/RLQu0rK7h4kbsBq5/arcgis/rest/services/Store_Locations/FeatureServer'
    mapped_record['latlng_source'] = 'Arc_Gis'
    mapped_record['snap'] = True
    mapped_record['food_bucks'] = True
    mapped_record['file_name'] = SOURCE
        
    return RulesEngine(mapped_record)\
        .apply_global_rules()\
        .apply_farmer_market_rules()\
        .apply_food_bank_rules()\
        .commit()

def main():
    """
    Main Function for Processing
    """
    # Retrieve the SNAP Locations from the ARC GIS Web Services
    logging.info(f"RETRIEVING SNAP LOCATIONS FROM WEB SERVICES...")
    locations = gis.get_snap_sites()
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(locations)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for location in locations:
        # Map the Record
        mapped_record = map_record(location, schema)

        # Add the Id
        mapped_record['id'] = row_number
        
        # Validate the record
        result = validation.validate(schema, mapped_record)
        if not result.get('valid', True):
            mapped_record['in_error'] = True
            mapped_record['data_issues'] = result.get('errors', '')
            error_records = error_records + 1

        # Add it to the Collection
        records.append(mapped_record)
        row_number = row_number + 1
    if records:
        logging.info(
            f"OUTPUTING SNAP LOCATIONS FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info('DONE PROCESSING RAW SNAP LOCATIONS SOURCE INFORMATION')


if __name__ == '__main__':
    main()
