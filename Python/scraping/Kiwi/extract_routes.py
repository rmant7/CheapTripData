#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv38/bin/python3.8
import gzip
import json
import pandas as pd
from pathlib import Path
import traceback


from config import OUTPUTS_DIR, LOCATIONS_PATH, TRANSPORT_TYPES_ID
from logger import logger_setup


logger = logger_setup(Path(__file__).stem, 'w')


def gen_routes_data():
    source_folder = Path(OUTPUTS_DIR)
    for file_path in source_folder.rglob('*.json.gz'):
        with gzip.open(file_path, 'r') as f:
            routes_data = json.load(f)
        yield routes_data['data']


def extract_routes() -> None:
    df_locations = pd.read_csv(Path(LOCATIONS_PATH), index_col='id')
    extracted_routes = set()  
    for route_data in gen_routes_data():
        for route in route_data:
            try:
                from_id, to_id = [df_locations.query('name == @city_name').index.values[0] for 
                                    city_name in (route['cityFrom'], route['cityTo'])]
                if from_id == to_id: continue
                print((from_id,
                        to_id,
                        TRANSPORT_TYPES_ID[route['route'][0]['vehicle_type']],
                        route['price'],
                        route['duration']['total'] // 60))
                extracted_routes.add((from_id,
                                 to_id,
                                 TRANSPORT_TYPES_ID[route['route'][0]['vehicle_type']],
                                 route['price'],
                                 route['duration']['total'] // 60))
            except IndexError:
                continue
    return extracted_routes
    
    
def process_routes(extracted_routes: set) -> pd.DataFrame:
    df_extracted_routes = pd.DataFrame(list(extracted_routes),
                                       columns=['from_id', 'to_id', 'transport_id', 'price_EUR', 'duration_min'])
    df_extracted_routes.sort_values(by=['from_id', 'to_id', 'transport_id', 'price_EUR'], ascending=True, inplace=True)
    df_extracted_routes.drop_duplicates(subset=['from_id', 'to_id', 'transport_id'], inplace=True, ignore_index=True)              
    return df_extracted_routes


def main():
    extracted_routes = extract_routes()
    df_processed = process_routes(extracted_routes)
    df_processed.to_csv(Path(f'{OUTPUTS_DIR}/extracted_routes.csv'), index=False)


if __name__ == '__main__':
    main()

    
  
    