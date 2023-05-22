import multiprocessing
import json
from time import perf_counter


from functions import get_prompts_GPT, get_response_GPT, get_cities
from config import SEO_FESTIVALS_DIR, PROMPTS_DIR


missing_cities = {"cities":[]}
def process_file(city, api_key, city_number):
    print(f'\nProcess: {city_number}, City: {city}')    
    prompts = get_prompts_GPT(PROMPTS_DIR/'events_festivals_seo_pmt.json')
    
    data = dict()
    try:
        data = json.loads(get_response_GPT(prompts['prompt'].format(city=city), api_key), strict=False)
    except Exception as error:
        missing_cities['cities'].append(city)
        print(f'\nDuring processing {city_number}.{city} there was an error: {error}')
    
    # write result in json
    SEO_FESTIVALS_DIR.mkdir(parents=True, exist_ok=True)  
    with open(f'{SEO_FESTIVALS_DIR}/{city}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)                    
    print(f'{city} processed successfully!')


def run_processes(key_numbers):
    # Get the list of cities
    cities = get_cities()

    # Get the list of API keys
    api_keys = [f'OPENAI_API_KEY_CT_{i + 2}' for i in range(key_numbers)]
    # api_keys = ['OPENAI_API_KEY']
    print(api_keys)

    # Create a pool of processes with as many workers as there are API keys
    pool = multiprocessing.Pool(len(api_keys))

    # Loop through the files and create a thread for each one
    for i, city in enumerate(cities):
        # Get the corresponding API key by cycling through the list
        api_key = api_keys[i % len(api_keys)]
        # Create a thread object with the target function and the file name and API key as arguments
        pool.apply_async(process_file, args=(city, api_key, i + 1))
        
    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

    with open(f'{SEO_FESTIVALS_DIR}/missing_cities.json', 'w') as json_file:
        json.dump(missing_cities, json_file)
    

if __name__ == '__main__':
    start = perf_counter()
    run_processes(1)
    #process_file()
    hours = (perf_counter() - start) // 3600
    remained_seconds = (perf_counter() - start) % 3600 
    print(f'\nTime elapsed: {hours} h {remained_seconds // 60} min.\n')
