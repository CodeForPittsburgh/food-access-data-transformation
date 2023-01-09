"""
Retrieves the Add New Sites Sheet from the PFPC Google Docs.    
"""

import csv
import json
import logging
import os

from helpers import gis, mapbox, maputil, validation
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'manual-sources-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'Manual Sources Google Sheets'
MAPBOX_KEY = os.environ.get('MAPBOX_KEY', 'none')

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


def get_coordinates(mapped_record: dict) -> dict:
    """
    Retrieves the Latitude and Longitude from the address.

    Args:
        record (dict): Commone Record

    Returns:
        dict: Lat/Long Dictionary
    """
    address = f"{mapped_record['address']},{mapped_record['city']},{mapped_record['state'],{mapped_record['zip_code']}}"
    return mapbox.get_coordinates(MAPBOX_KEY, address)


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
        record (dict): Sheet Record

    Returns:
        dict: Mapped Record
    """
    mapped_record = maputil.new_record(schema)

    mapped_record['file_name'] = SOURCE
    mapped_record['name'] = record.get('name', '')
    mapped_record['type'] = record.get('type', 'unknown')
    mapped_record['address'] = record.get('address', '')
    mapped_record['city'] = record.get('city', '')
    mapped_record['state'] = record.get('state', '')
    mapped_record['zip_code'] = record.get('zip_code', '')
    mapped_record['county'] = record.get('county', '')
    mapped_record['location_description'] = str(record.get(
        'location_description', '')).replace('\n', '<br/>').replace('\r', '<br/>')
    mapped_record['phone'] = record.get('phone', '')
    mapped_record['url'] = record.get('url', '')
    mapped_record['date_from'] = record.get('date_from', '')
    mapped_record['date_to'] = record.get('date_to', '')
    mapped_record['open_to_spec_group'] = record.get('open_to_spec_group', '')
    mapped_record['food_rx'] = maputil.convert_value(
        record.get('food_rx', 'no'), 'boolean')
    mapped_record['wic'] = maputil.convert_value(
        record.get('wic', 'no'), 'boolean')
    mapped_record['snap'] = maputil.convert_value(
        record.get('snap', 'no'), 'boolean')
    mapped_record['food_bucks'] = maputil.convert_value(
        record.get('food_bucks', 'no'), 'boolean')
    mapped_record['fmnp'] = maputil.convert_value(
        record.get('fmnp', 'no'), 'boolean')
    mapped_record['fresh_produce'] = maputil.convert_value(
        record.get('fresh_produce', 'no'), 'boolean')
    mapped_record['free_distribution'] = maputil.convert_value(
        record.get('free_distribution', 'no'), 'boolean')
    mapped_record['source_org'] = 'PFPC'
    mapped_record['source_file'] = SOURCE

    # Get the Coordinates
    coordinates = get_coordinates(mapped_record)
    if coordinates:
        mapped_record['longitude'] = coordinates.get('longitude', 0)
        mapped_record['latitude'] = coordinates.get('latitude', 0)
        mapped_record['latlng_source'] = 'MapBox GeoCode'

    return RulesEngine(mapped_record)\
        .apply_global_rules()\
        .apply_farmer_market_rules()\
        .apply_food_bank_rules()\
        .apply_summer_meal_rules()\
        .commit()


def main():
    """
    Main Function for Processing
    """
    # Retrieve the Bridgeway Captial locaations from the Google Sheet
    logging.info(f"RETRIVING MANUAL SOURCES FROM GOOGLE SHEET...")
    locations = gis.get_google_sheet_csv(
        '1QwWXDMzNc7X-krErCwuzTHgXfiru-U99jJeJ6nk9hko', '693210073')
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(locations)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for location in locations:
        # Map the Record
        mapped_record = map_record(location, schema)

        if mapped_record:
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
            f"OUTPUTING MANUAL SOURCES FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info(
        'DONE PROCESSING RAW MANUAL SOURCES INFORMATION')


if __name__ == '__main__':
    main()
