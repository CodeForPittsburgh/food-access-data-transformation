"""
Converts the information from GP_garden_directory_listing CSV file to the common data model.
"""

import csv
import json
import logging
import os
from helpers import maputil, validation

from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'grow-pgh-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'food-data/PFPC_data_files/GP_garden_directory_listing-20210322.csv'

IN_DELIMITER = ','
OUT_DELIMITER = '|'

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
    
    csv.register_dialect('output', delimiter=OUT_DELIMITER)
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
    mapped_record['file_name'] = os.path.basename(SOURCE)
    mapped_record['name'] = record.get('content_post_title', '')
    mapped_record['address'] = record.get('directory_location__address', '')
    mapped_record['city'] = record.get('directory_location__city', '')
    mapped_record['state'] = record.get('directory_location__state', '')
    mapped_record['zip_code'] = record.get('directory_location__zip', '')
    mapped_record['latitude'] = float(record.get('directory_location__lat', 0))
    mapped_record['longitude'] = float(
        record.get('directory_location__lng', 0))
    mapped_record['location_description'] = record.get(
        'directory_category', '')
    mapped_record['type'] = 'grow pgh garden'
    mapped_record['phone'] = record.get('directory_contact__phone', '')
    mapped_record['url'] = record.get('directory_contact__website', '')
    mapped_record['source_org'] = 'Grow Pittsburgh'
    mapped_record['source_file'] = os.path.basename(SOURCE)
    mapped_record['latlng_source'] = 'Grow Pittsburgh'

    return RulesEngine(mapped_record).apply_global_rules().apply_grow_pgh_rules().commit()


def load_csv(path: str) -> list:
    """
    Loads the CSV to a dictionary list.

    Args:
        path (str): path to CSV

    Returns:
        list: List of Dictionary records.
    """

    csv.register_dialect('input', delimiter=IN_DELIMITER)
    records = []
    with open(path, 'r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file, dialect='input')
        for record in reader:
            records.append(record)
    return records


def main():
    """
    Main Function for Processing
    """
    # Retrieve the Grow PGH Items from the CSV FILE
    logging.info(f"LOADING GROW PGH CSV...")
    gardens = load_csv(SOURCE)
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(gardens)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for garden in gardens:
        # Map the Record
        mapped_record = map_record(garden, schema)

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
            f"OUTPUTING GROW PGH FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info('DONE PROCESSING RAW GROW PGH SOURCE INFORMATION')


if __name__ == '__main__':
    main()
