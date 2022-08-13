"""
De-Duplicates the merged data set
"""

import csv
import json
import logging
import os
import ndjson

from helpers import merge

MERGED_FOLDER = 'food-data/merged-data'

MERGE_FILE = os.path.join(MERGED_FOLDER, 'merged-raw-sources.csv')
OUTPUT_FILE = os.path.join(MERGED_FOLDER, 'deduped-merged-data.csv')
DUPLICATE_FILE = os.path.join(MERGED_FOLDER, 'duplicate-merged-data.csv')
NDJSON_FILE = os.path.join(MERGED_FOLDER, 'deduped-merged-data.ndjson')
SCHEMA_FILE = 'food-data/schema/map-data-schema.json'

logging.basicConfig(level=logging.INFO)


def load_schema(path: str) -> dict:
    """
    Loads the Schema File to a dictionary.

    Args:
        path (str): Schema File Path

    Returns:
        dict: Schema Dictionry
    """

    with open(path, 'r', encoding='utf-8') as input_file:
        return json.loads(input_file.read())


def load_file(path: str) -> list:
    """
    Loads the CSV File to a List of Dictionaries

    Args:
        path (str): CSV Path

    Returns:
        list: List of Dictionaries
    """

    records = []
    csv.register_dialect('input', delimiter='|')
    with open(path, 'r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file, dialect='input')
        for record in reader:
            records.append(record)
    return records


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


def output_results(path: str, records: list, columns: list) -> None:
    """
    Outputs the Records to a CSV file at the provided path.

    Args:
        path (str): Output Path
        records (list): Records to output.
    """

    csv.register_dialect('output', delimiter='|')
    with open(path, 'w', newline='', encoding='utf-8') as out_file:
        writer = csv.DictWriter(out_file, fieldnames=columns, dialect='output')
        writer.writeheader()
        writer.writerows(records)

def output_ndjson(path: str, records: list) -> None:
    """
    Outputs the records to a NDJSON file.

    Args:
        path (str): Output Path
        records (list): Records to output
    """
    
    with open(path, 'w', encoding='utf-8') as output_file:
        ndjson.dump(records, output_file)

def main():
    """
    Main Processing Functions
    """

    logging.info(f"DEDUPLICATING FILE {MERGE_FILE}...")

    schema = load_schema(SCHEMA_FILE)
    records = load_file(MERGE_FILE)
    
    if not os.path.exists(MERGED_FOLDER):
        os.makedirs(MERGED_FOLDER)

    if records:
        result = merge.deduplicate(records, schema)
        if result:
            logging.info('OUTPUTTING RESULTS...')
            columns = get_columns(schema)

            clean_recs = result.get('records', [])
            dupe_recs = result.get('duplicates', [])

            if clean_recs:
                logging.info(f"OUTPUTTING CLEANED RECORDS: {OUTPUT_FILE}")
                output_results(OUTPUT_FILE, clean_recs, columns)
                logging.info(f" OUTPUTTING CLEANED RECORDS TO NDJSON: {NDJSON_FILE}")
                output_ndjson(NDJSON_FILE, clean_recs)
                
            if dupe_recs:
                logging.info(f"OUTPUTING DUPLICATE RECORDS: {DUPLICATE_FILE}")
                output_results(DUPLICATE_FILE, dupe_recs, columns)

    logging.info('DONE')


if __name__ == '__main__':
    main()
