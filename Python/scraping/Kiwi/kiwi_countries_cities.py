#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv312/bin/python3.12
from concurrent.futures import ThreadPoolExecutor
import requests
import json
from datetime import datetime
from pathlib import Path
from functions import limit_calls_per_minute, rate_limited, elapsed_time
from config import INPUTS_DIR, OUTPUTS_DIR, BASE_URL, HEADERS, \
                    API_LOCATIONS_SUBENTITY, API_LOCATIONS_DUMP, \
                    EXCLUDED_COUNTRIES, COUNTED_COUNTRIES
from logger import logger_setup


timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = logger_setup(f'{Path(__file__).stem}')

SESSION = requests.session()


def save_json(data: dict, filename: str) -> None:
    with open(f'{OUTPUTS_DIR}/{filename}.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f'{filename}.json saved')
            

def get_all_countries():
    try:
        response = SESSION.get(BASE_URL + API_LOCATIONS_DUMP,
                                headers=HEADERS,
                                params={
                                   'locale': 'en-US',
                                   'location_types': 'country',
                                   'limit': 300,
                                   'sort': 'name',                                
                                }
                            )
        response.raise_for_status()
        return response.json()
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')    
   
        
def gen_country_id_name_pairs():
    with open(f'{INPUTS_DIR}/kiwi_countries.json', 'r') as f:
        countries = json.load(f)
        for country in countries['locations']:
            # if country['id'] in EXCLUDED_COUNTRIES: continue
            logger.info(f'Processing: {country["id"], country["name"]}')
            yield country['id'], country['name']
    
    
def data_filter(data: dict, country_id: str) -> None:
    data['locations'] = [{k: v for k, v in item.items() if k != 'alternative_departure_points'} 
                         for item in data['locations']]
    save_json(data, country_id)
    
            
@rate_limited(limit=20, per=60)
def get_cities_by_country(country_id_name: tuple) -> None:
    country_id, country_name = country_id_name
    logger.info(f'Getting cities for: {country_name}')
    try:
        response = SESSION.get(BASE_URL + API_LOCATIONS_SUBENTITY,
                                headers=HEADERS,
                                params={
                                   'term': country_id,
                                   'location_types': 'city',
                                   'limit': 1000,
                                   'sort': 'name',                                
                                }
                            )
        response.raise_for_status()
        data_filter(response.json(), country_id)
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')


@elapsed_time
def main():
    try:
        logger.info('Process is started...')
        with ThreadPoolExecutor() as executor:
            executor.map(get_cities_by_country, gen_country_id_name_pairs())
        logger.info('Process is completed: SUCCESS')
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')


if __name__ == '__main__':
    # main()
    ...  
    
    
    