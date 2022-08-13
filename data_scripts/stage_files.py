"""
Script to Stage the files for the data source.
"""

import logging
import os
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO)

ARCHIVE_DIRECTORY = 'food-data/archive/'
DESTINATION_DIRECTORY = 'food-data/processed-datasets'
SOURCE_FILE = 'food-data/merged-data/deduped-merged-data.csv'
OUTPUT_FILE = os.path.join(DESTINATION_DIRECTORY, 'merged_datasets.csv')
NDJSON_FILE = 'food-data/merged-data/deduped-merged-data.ndjson'
NDJSON_OUTPUT_FILE = os.path.join(DESTINATION_DIRECTORY, 'merged_datasets.ndjson')


def archive_file(path: str, archive_path: str) -> None:
    """
    Archives the previous version to the archive directory.

    Args:
        path (str): Path to the File to Archive
        archive_path(str): Path to Archive location
    """

    if not os.path.exists(archive_path):
        os.makedirs(archive_path)

    if os.path.exists(path):
        logging.info(f"ARCHIVING FILE {path}")
        file_name = os.path.basename(path).replace(
            '.csv', '') + datetime.now().strftime('%Y.%m.%d-%H.%M.%S') + '.csv'
        shutil.move(path, os.path.join(archive_path, file_name))


def main():
    """
    Main Scipt for moving the files.
    """
    logging.info('STAGING PROCESSED FILE...')
    
    if not os.path.exists(DESTINATION_DIRECTORY):
        os.makedirs(DESTINATION_DIRECTORY)
    
    if os.path.exists(SOURCE_FILE):
        archive_file(OUTPUT_FILE, ARCHIVE_DIRECTORY)
        logging.info(f"MOVING NEW DATASET FILES INTO PLACE..")
        shutil.move(SOURCE_FILE, OUTPUT_FILE)
        shutil.move(NDJSON_FILE, NDJSON_OUTPUT_FILE)
        
    else:
        logging.error(f"NEW DATASET FILE DOES NOT EXIST: {SOURCE_FILE}")
        raise EnvironmentError('NO NEW SOURCE FILE EXISTS')

    logging.info('DONE')


if __name__ == '__main__':
    main()
