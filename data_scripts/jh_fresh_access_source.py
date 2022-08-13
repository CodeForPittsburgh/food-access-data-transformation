"""
Retrieves the Just Harvest Fresh Corners Store 
Google Docs.    
"""

import csv
import json
import logging
import os


from helpers import gis, maputil, validation, mapbox
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'jh-fresh-access-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'Just Harvest Google Sheets'
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
    Retrieves the Latitude and Longitude from the address or cross street

    Args:
        record (dict): Commone Record

    Returns:
        dict: Lat/Long Dictionary
    """
    search = f"{mapped_record['address']},{mapped_record['city']},{mapped_record['state']}"
    return mapbox.get_coordinates(MAPBOX_KEY, search)


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
    mapped_record['name'] = record.get("Market", '')
    mapped_record['city'] = record.get('city', '')
    mapped_record['state'] = record.get('state', '')
    mapped_record['zip_code'] = record.get('zip_code', '')
    mapped_record['county'] = 'Allegheny'
    mapped_record['type'] = 'fresh access'
    mapped_record['location_description'] = f"{record.get('Season', '')}<br/>{record.get('Date/Time', '')}"
    mapped_record['source_org'] = 'Just Harvest'
    mapped_record['source_file'] = SOURCE
    mapped_record['latlng_source'] = 'MapBox GeoCode'

    # Build Address from Stree One/Two or Address
    if record.get('address',  ''):
        mapped_record['address'] = record.get('address')
    else:
        mapped_record['address'] = f"{record.get('street_one')} and {record.get('street_two')}"

    # Set Start/End
    parts = str(record.get('Season')).split('-')
    mapped_record['date_from'] = parts[0]
    mapped_record['date_to'] = parts[1]

    # Get the Coordinates

    coordinates = get_coordinates(mapped_record)
    if coordinates:
        mapped_record['longitude'] = coordinates.get('longitude', 0)
        mapped_record['latitude'] = coordinates.get('latitude', 0)

    return RulesEngine(mapped_record).apply_global_rules().apply_fresh_access_rules().commit()


def main():
    """
    Main Function for Processing
    """
    # Retrieve the Fresh  Access Locations from the Google Sheet
    logging.info(f"RETRIVING FRESH ACCESS LOCATIONS FROM GOOGLE SHEET...")
    locations = gis.get_google_sheet_csv(
        '1QwWXDMzNc7X-krErCwuzTHgXfiru-U99jJeJ6nk9hko', '790266249')
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
            f"OUTPUTING FRESH ACCESS LOCATIONS FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info(
        'DONE PROCESSING RAW FRESH ACCESS LOCATIONS SOURCE INFORMATION')


if __name__ == '__main__':
    main()
