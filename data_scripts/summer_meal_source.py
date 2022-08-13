"""
Retrieves the Information from the Farmer's Market
Nutrition Program from the ARC GIS File.    
"""

import csv
import json
import logging
import datetime
import os

from helpers import gis, maputil, validation
from helpers.rules import RulesEngine

RAW_OUTPUT_FOLDER = 'food-data/raw-sources'
RAW_OUTPUT_FILE = 'summer-meal-raw.csv'
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'
SOURCE = 'ARC_GIS_SUMMER_MEAL_QUERY'

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
    mapped_record['name'] = record.get('Site_Name', '')
    mapped_record['address'] = record.get('Site_Street', '')
    mapped_record['city'] = record.get('Site_City', '')
    mapped_record['state'] = record.get('Site_State', '')
    mapped_record['zip_code'] = record.get('Site_Zip', '')
    mapped_record['latitude'] = record.get('Latitude', 0)
    mapped_record['longitude'] = record.get('Longitude', 0)
    mapped_record['type'] = 'summer meal site'
    mapped_record['county'] = record.get('Site_County', '')
    mapped_record['original_id'] = str(record.get('Site_ID_External', ''))
    mapped_record['source_org'] = 'Allegheny County'
    mapped_record['source_file'] = 'https://services1.arcgis.com/vdNDkVykv9vEWFX4/arcgis/rest/services/Child_Nutrition/FeatureServer'
    mapped_record['latlng_source'] = 'Arc_Gis'
    mapped_record['free_distribution'] = True
    mapped_record['file_name'] = SOURCE
    mapped_record['open_to_spec_group'] = 'children and teens 18 and younger'
        
    # Merge the Location Description
    desc = ''
    if record.get('Site_Street2', None):
        desc = f"Site Location Info: {record.get('Site_Street2')}<br/>"
    
    if record.get('Service_Type', None):
        desc = f"{desc}Service Type: {record.get('Service_Type')}<br/>"
    
    if record.get('Site_Hours', None):
        desc = f"{desc}Site Hours: {record.get('Site_Hours')}<br/>"
    
    if record.get('Comments', None):
        desc = f"{desc}Comments: {record.get('Comments')}<br/>"
    
    if record.get('Site_Instructions', None):
        desc = f"{desc}Site Instructions: {record.get('Site_Instructions')}"
    
    mapped_record['location_description'] = desc
    
    if record.get('Start_Date', None):
        mapped_record['date_from'] = datetime.datetime.fromtimestamp(record.get('Start_Date')/1000).strftime('%B %d, %Y')
    
    if record.get('End_Date', None):
        mapped_record['date_to'] = datetime.datetime.fromtimestamp(record.get('End_Date')/1000).strftime('%B %d, %Y')
    
    return RulesEngine(mapped_record)\
        .apply_global_rules()\
        .apply_summer_meal_rules()\
        .commit()

def main():
    """
    Main Function for Processing
    """
    # Retrieve the Summer Meal Sites from the ARC GIS Web Services
    logging.info(f"RETRIVING SUMMER MEAL SITES FROM WEB SERVICES...")
    sites = gis.get_summer_meal_sites()
    schema = load_schema(SCHEMA_FILE)
    logging.info(f"RETRIEVED {len(sites)} ENTRIES TO CONVERT.")
    records = []
    error_records = 0
    row_number = 0
    logging.info('CONVERTING ENTRIES TO COMMON RECORD DEFINITION...')
    for site in sites:
        # Map the Record
        mapped_record = map_record(site, schema)
        
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
            f"OUTPUTING SUMMER MEAL SITE FILE: {RAW_OUTPUT_FILE} WITH {error_records} ERRORS.")
        write_output(records)
    logging.info('DONE PROCESSING RAW SUMMER MEAL SITE SOURCE INFORMATION')


if __name__ == '__main__':
    main()
