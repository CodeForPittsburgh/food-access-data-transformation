"""
Merges the cleaned prep csv files to a single Source file for the Web Site.
"""

import csv
import json
import logging
import os

from helpers import validation

logging.basicConfig(level=logging.INFO)

SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
INPUT_DIRECTORY = 'food-data/raw-sources'

OUTPUT_DIRECTORY = 'food-data/merged-data'
OUTPUT_FILE = 'merged-raw-sources.csv'
INVALID_FILE = 'invalid-raw-sources.csv'

DELIMITER = '|'


def get_schema(path: str) -> dict:
    """
    Loads the JSON Schema from the file.

    Args:
        path (str): path to the schema

    Returns:
        dict: Dictionary of Schema
    """

    with open(path, 'r', encoding='utf-8') as input_file:
        return json.loads(input_file.read())


def get_columns(schema: dict) -> list:
    """
    Creates a column list from the schema.

    Args:
        schema (dict): JSON Schema

    Returns:
        list: list of columns names
    """

    properties = schema.get('properties', {})
    columns = []
    for key in properties.keys():
        columns.append(key)
    return columns


def validate_coordinates(record: dict):
    """
    Validates that the coordinates are in the correct range.

    Args:
        record (dict): Sets the Latitude and Longitude to 0 if not valid.
    """

    if not validation.validate_latitude(float(record.get('latitude', 0))) or not validation.validate_longitude(float(record.get('longitude', 0))):
        data_issues = f"{record.get('data_issues', '')};Invalid Lat/Long:{record.get('latitude')}/{record.get('longitude')}"
        record['data_issues'] = data_issues
        record['longitude'] = 0
        record['latitude'] = 0
        record['in_error'] = True


def main():
    """
    Merges the files together into a single raw file.
    """

    logging.info(f"MERGING RAW FILES IN {INPUT_DIRECTORY}")
    logging.info(f"LOADING SCHEMA: {SCHEMA_FILE}")

    schema = get_schema(SCHEMA_FILE)
    columns = get_columns(schema)

    csv.register_dialect('input', delimiter=DELIMITER)

    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

    files = os.listdir(INPUT_DIRECTORY)
    records = []
    invalid_records = []
    for file in files:
        path = os.path.join(INPUT_DIRECTORY, file)
        logging.info(f"MERGING FILE {file}")
        with open(path, 'r', encoding='utf-8') as input_file:
            reader = csv.DictReader(input_file, dialect='input')
            for record in reader:
                validate_coordinates(record)
                if record.get('longitude', 0) != 0 and record.get('latitude', 0) != 0 and record.get('active_record', False):
                    records.append(record)
                else:
                    invalid_records.append(record)

    if invalid_records:
        logging.info(f"OUTPUTING INVALID RAW RECORDS {INVALID_FILE}")
        with open(os.path.join(OUTPUT_DIRECTORY, INVALID_FILE), 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(
                output_file, fieldnames=columns, dialect='input')
            writer.writeheader()
            writer.writerows(invalid_records)
    if records:
        logging.info(f"OUTPUTING MERGED RAW FILE {OUTPUT_FILE}")
        with open(os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE), 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(
                output_file, fieldnames=columns, dialect='input')
            writer.writeheader()
            writer.writerows(records)

    logging.info('DONE')


if __name__ == '__main__':
    main()
