"""
Retrieves the WIC Locations from the PA WIC Service.    
"""

import csv
import json
import logging
import os


from helpers import gis, maputil, validation, mapbox, classification
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'wic-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'WIC_WS_QUERY'
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
    mapped_record['name'] = record.get('StoreName', '')
    mapped_record['city'] = record.get('City', '')
    mapped_record['state'] = record.get('State', '')
    mapped_record['zip_code'] = record.get('ZipCode', '')
    mapped_record['county'] = 'Allegheny'    
    mapped_record['source_org'] = 'PA WIC'
    mapped_record['source_file'] = 'https://www.pawic.com'
    mapped_record['latlng_source'] = 'MapBox GeoCode'
    mapped_record['address'] = record.get('StreetAddrLine1', '')
    mapped_record['url'] = record.get('Directions', '')
    mapped_record['phone'] = record.get('PhoneNr', '')
    mapped_record['wic'] = True

    #Classify the Record
    mapped_record['type'] = classification.find_type(mapped_record['name'])
    
    # Get the Coordinates

    coordinates = get_coordinates(mapped_record)
    if coordinates:
        mapped_record['longitude'] = coordinates.get('longitude', 0)
        mapped_record['latitude'] = coordinates.get('latitude', 0)

    return RulesEngine(mapped_record)\
        .apply_global_rules()\
        .apply_farmer_market_rules()\
        .apply_food_bank_rules()\
        .commit()


def main():
    """
    Main Function for Processing
    """
    # Retrieve the WIC Locations from PA WIC
    logging.info(f"RETRIVING WIC LOCATIONS FROM PA WIC SERVICES...")
    locations = gis.get_wic_sites()
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
            f"OUTPUTING WIC LOCATIONS FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info(
        'DONE PROCESSING RAW WIC LOCATIONS SOURCE INFORMATION')


if __name__ == '__main__':
    main()
