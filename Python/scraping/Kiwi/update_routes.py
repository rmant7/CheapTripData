#!/home/azureuser/ChipTripData/Python/scraping/Kiwi/.venv38/bin/python3.8
import pandas as pd
from pathlib import Path
import traceback


from config import OUTPUTS_DIR, ROUTES_PATH
from logger import logger_setup


logger = logger_setup(Path(__file__).stem, 'w')


def update_routes():
    columns_names = ('from_id', 'to_id', 'transport_id', 'price_EUR', 'duration_min')
    dict_dtypes = {k:'Int32' for k in columns_names} # allows to save data as integer not as float (by default)
    
    df_routes = pd.read_csv(Path(ROUTES_PATH), usecols=columns_names, dtype=dict_dtypes)
    df_extracted_routes = pd.read_csv(Path(f'{OUTPUTS_DIR}/extracted_routes.csv'), dtype=dict_dtypes)
    
    # updating via merge and following combine_first
    df_merged = pd.merge(df_routes, df_extracted_routes, how='outer', on=['from_id', 'to_id', 'transport_id'])
    df_merged['price_EUR'] = df_merged['price_EUR_y'].combine_first(df_merged['price_EUR_x'])
    df_merged['duration_min'] = df_merged['duration_min_y'].combine_first(df_merged['duration_min_x'])
    df_merged.drop(['price_EUR_x', 'price_EUR_y', 'duration_min_x', 'duration_min_y'], axis=1, inplace=True)
    df_merged.sort_values(by=['from_id', 'to_id', 'transport_id', 'price_EUR'], ascending=True, inplace=True)
    
    # setting 'path_id'    
    df_result = pd.DataFrame()
    for id in df_merged['from_id'].unique():
        df_temp = df_merged.query('from_id == @id')
        df_temp.reset_index(drop=True, inplace=True)
        df_temp.insert(0, 'path_id', df_temp['from_id'] * 10000 + df_temp.index + 1)
        df_result = pd.concat([df_result, df_temp])   
    
    print(df_result)
    df_result.to_csv(Path(f'{OUTPUTS_DIR}/routes_upd_140124.csv'), index=False)


def main():
    update_routes()


if __name__ == '__main__':
    main()

    
  
    