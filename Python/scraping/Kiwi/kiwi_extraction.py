#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv312/bin/python3.12
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import gzip
from io import BytesIO
from itertools import permutations, cycle, product
import json
from pathlib import Path
import requests
import traceback


import functions
from config import INPUTS_DIR, OUTPUTS_DIR, BASE_URL, HEADERS, \
                    EXCLUDED_COUNTRIES, API_SEARCH, DATE_FROM, DATE_TO, VEHICLE_TYPES, \
                    MAX_CALLS_PER_API, PERIOD_API_CALL, COUNTED_COUNTRIES, BATCH_SIZE
from logger import logger_setup


def has_limit_routes_number(data: dict, limit: int=200) -> bool:
    if data['_results'] == limit:
        return True
    return False





def main(source: str='aircraft_04_01_24'):
    source_folder = Path(f'{OUTPUTS_DIR}/{source}')
    for file_path in source_folder.glob('*.json.gz'):
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
                
        # if has_limit_routes_number(data):
        #     print(file_path.stem.split('.')[0], data['_results'])




if __name__ == '__main__':
    main()