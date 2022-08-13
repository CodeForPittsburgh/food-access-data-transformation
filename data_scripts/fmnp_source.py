"""
Retrieves the Information from the Farmer's Market
Nutrition Program from the ARC GIS File.    
"""

import csv
import json
import logging
import os

from helpers import gis, maputil, validation
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'fmnp-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'ARC_GIS_FMNP_QUERY'

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
    mapped_record['name'] = record.get('MarketName')
    mapped_record['address'] = record.get('Address1')
    mapped_record['city'] = record.get('City')
    mapped_record['state'] = record.get('StateCode')
    mapped_record['zip_code'] = record.get('Zip')
    mapped_record['latitude'] = record.get('Latitude')
    mapped_record['longitude'] = record.get('Longitude')
    mapped_record['type'] = "farmer's market"
    mapped_record['county'] = record.get('FarmMarketCounty')
    mapped_record['phone'] = record.get('MarketPhone')
    mapped_record['original_id'] = str(record.get('FarmMarketID'))
    mapped_record['source_org'] = 'FMNP Markets'
    mapped_record['source_file'] = 'https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer'
    mapped_record['latlng_source'] = 'Arc_Gis'
    mapped_record['fmnp'] = True

    return RulesEngine(mapped_record)\
        .apply_global_rules()\
        .apply_farmer_market_rules()\
        .commit()


def set_schedule(record: dict) -> dict:
    """
    Retrieves the Vendor Schedules for the item and sets the Date_From, Date_To and Location_Description

    Args:
        record (dict): Commone Record

    Returns:
        dict: Updated Record
    """
    market_id = record.get('original_id')
    schedules = gis.get_schedule_entry(market_id)

    record = maputil.merge_location_description(record, schedules)
    record = maputil.set_date_range(record, schedules)
    return record


def main():
    """
    Main Function for Processing
    """
    # Retrieve the FMNP Markets from the ARC GIS Web Services
    logging.info(f"RETRIVING FARMER'S MARKETS FROM WEB SERVICES...")
    markets = gis.get_fmnp_markets()
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(markets)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for market in markets:
        # Map the Record
        mapped_record = map_record(market, schema)

        # Set the Schedule
        mapped_record = set_schedule(mapped_record)

        # Add the Id
        mapped_record['id'] = row_number
        mapped_record['file_name'] = SOURCE
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
            f"OUTPUTING FMNP FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info('DONE PROCESSING RAW FMNP SOURCE INFORMATION')


if __name__ == '__main__':
    main()
