#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv312/bin/python3.12
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import gzip
from itertools import product
import json
from pathlib import Path
import requests
import traceback


from config import INPUTS_DIR, OUTPUTS_DIR, BASE_URL, HEADERS, \
                    EXCLUDED_COUNTRIES, API_SEARCH, DATE_FROM, DATE_TO, VEHICLE_TYPES, \
                    MAX_CALLS_PER_API, PERIOD_API_CALL, COUNTED_COUNTRIES, BATCH_SIZE
import functions
from logger import logger_setup


timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = logger_setup(Path(__file__).stem, 'w')

SESSION = requests.session()

# custom Exceptions to apart them from the exceptions raised in main()
class FuncException(Exception):
    pass


def save_json(data: dict, from_: str, to_: str, vehicle_type: str) -> None:
    try:
        output_folder = Path(f'{OUTPUTS_DIR}/{vehicle_type}')
        output_folder.mkdir(parents=True, exist_ok=True)
        file_name = f'{from_}__{to_}.json.gz'
        file_path = Path(f'{output_folder}/{file_name}')
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f'Saved to: {file_name}')
    except Exception as err:
        logger.error(f'''There was an error {type(err).__name__} while saving json: {file_name}:
                        {traceback.format_exc()}''')
        raise FuncException from err

 
def process_response(from_: str, to_: str, routes: bytes, vehicle_type: str):
    try:
        routes = json.loads(routes.decode("utf-8"))
        if routes['_results'] != 0:
            save_json(routes, from_, to_, vehicle_type)
        else:
            logger.info(f'There are not any {vehicle_type} routes between {from_} and {to_}')
    except Exception as err:
        logger.error(f'''There was an error {type(err).__name__} while processing response: {from_} - {to_}:
                        {traceback.format_exc()}''')
        raise FuncException from err
      

@functions.rate_limited(limit=MAX_CALLS_PER_API, per=PERIOD_API_CALL)
def get_routes(from_: str, to_: str, vehicle_type: str) -> None:
    try:
        logger.info(f'Getting {vehicle_type} routes for: {from_} - {to_}...')
        response = SESSION.get(BASE_URL + API_SEARCH,
                                headers=HEADERS,
                                params={
                                        'fly_from': from_,
                                        'fly_to': to_,
                                        'date_from': DATE_FROM,
                                        'date_to': DATE_TO,
                                        'one_for_city': 1, # returns the cheapest flight to the city covered by the 'fly_to'
                                        'one_per_date': 1, # returns the cheapest flight for each date in the range defined 
                                                        # by 'date_from' and date_to '''
                                        'adults': 1, 
                                        'locale': 'en',
                                        'vehicle_type': vehicle_type,
                                        'sort': 'price',
                                        'limit': 1000,                        
                                }
        )
        response.raise_for_status()
        process_response(from_, to_, response.content, vehicle_type)
    except Exception as err:
        logger.error(f'''There was an error {type(err).__name__} while getting routes: {from_} - {to_}:
                        {traceback.format_exc()}''')
        raise FuncException from err


def get_countries_by_continent(continent_codes: list=['EU']):
    file_path = f'{INPUTS_DIR}/kiwi_countries.json'
    try:
        with open(file_path, 'r') as f:
            locations = json.load(f)
        countries = [country['id'] for country in locations['locations'] if 
                        country['continent']['code'] in continent_codes and
                        country['id'] not in EXCLUDED_COUNTRIES 
        ]
        return countries
    except Exception as err:
        logger.error(f'''There was an error {type(err).__name__} while getting list of countries from: {file_path}:
                        {traceback.format_exc()}''')
        raise FuncException from err


@functions.elapsed_time
def main(vehicle_type: str='aircraft'):
    logger.info(f'Process started for {vehicle_type.upper()}')
    countries = get_countries_by_continent() + COUNTED_COUNTRIES
    routes = tuple(product(countries, repeat=2))
    for i in range(0, len(routes), BATCH_SIZE):
        batched_routes = routes[i : i + BATCH_SIZE]
        try:
            with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
                _ = [executor.submit(get_routes, *route, vehicle_type) for route in batched_routes]
        except FuncException:
            continue
        except Exception as err:
            logger.error(f'{type(err).__name__}: {err}')
            continue
    logger.info(f'Process completed for {vehicle_type.upper()}: SUCCESS')

        
if __name__ == '__main__':
    _ = list(map(main, VEHICLE_TYPES))
    

        