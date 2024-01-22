#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv38/bin/python3.8
from csv import writer
import gzip
import json
import pandas as pd
from pathlib import Path
import traceback


from config import OUTPUTS_DIR, LOCATIONS_PATH, TRANSPORT_TYPES_ID, EXTRACTED_ROUTES_FILE_NAME, LOCATIONS_EXT_PATH
from logger import logger_setup


logger = logger_setup(Path(__file__).stem, 'w')


def gen_routes_data(source: str) -> dict:
    source_folder = Path(f'{OUTPUTS_DIR}/{source}')
    for file_path in source_folder.rglob('*.json.gz'):
        with gzip.open(file_path, 'r') as f:
            routes = json.load(f)
        yield routes['data']


def extract_routes(source: str) -> None:
    df_locations_ext = pd.read_csv(Path(LOCATIONS_EXT_PATH), index_col='id')
    inner_jsons_dir = Path(f'{OUTPUTS_DIR}/{source}/inner_jsons')
    inner_jsons_dir.mkdir(parents=True, exist_ok=True)
    path_id = {v: 10000 * v for v in df_locations_ext.index.values}
    triples = set()
    csv_path = Path(f'{OUTPUTS_DIR}/{source}/{EXTRACTED_ROUTES_FILE_NAME}')
    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = writer(csvfile)
        for route_data in gen_routes_data(source):
            for route in route_data:
                try:
                    from_id, to_id = [df_locations_ext.query('name == @city_name').index.values[0] for 
                                        city_name in (route['cityFrom'], route['cityTo'])]
                    
                    vehicle_id = TRANSPORT_TYPES_ID[route['route'][0]['vehicle_type']]
                    
                    if from_id == to_id or (from_id, to_id, vehicle_id) in triples: 
                        continue
                        
                    triples.add((from_id, to_id, vehicle_id))
                    
                    path_id[from_id] += 1
                    price = route['price']
                    duration = route['duration']['total'] // 60
                    
                    with open(Path(f'{inner_jsons_dir}/{path_id[from_id]}.json'), 'w') as jsonfile:
                        json.dump(route, jsonfile, indent=4)
                        
                    csv_writer.writerow((path_id[from_id], from_id, to_id, vehicle_id, price, duration))
                    
                except IndexError:
                    continue
    
    
def process_csv(source: str) -> None:
    csv_path = Path(f'{OUTPUTS_DIR}/{source}/{EXTRACTED_ROUTES_FILE_NAME}')
    df_extracted_routes = pd.read_csv(csv_path, header=None,
                                       names=['path_id', 'from_id', 'to_id', 'transport_id', 'price_EUR', 'duration_min'])
    df_extracted_routes.sort_values(by=['from_id', 'to_id', 'transport_id', 'price_EUR'], ascending=True, inplace=True)
    df_extracted_routes.drop_duplicates(subset=['from_id', 'to_id', 'transport_id'], inplace=True, ignore_index=True)
    df_extracted_routes.to_csv(csv_path, index=False)            
    


def main(source: str):
    # extract_routes(source)
    process_csv(source)


if __name__ == '__main__':
    main('run_2')

    
  
    