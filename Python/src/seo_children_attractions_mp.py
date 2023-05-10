import multiprocessing
import json
from pathlib import Path
from time import perf_counter
import functools

from functions import get_prompts_GPT, get_response_GPT, get_cities
from config import PROMPTS_DIR, SEO_CHILDREN_ATTRACTIONS_DIR, CHILDREN_ATTRACTIONS_LIST_DIR


def recursive_replace(d, old_str, new_str):
    for k, v in d.items():
        if isinstance(v, dict):
            recursive_replace(v, old_str, new_str)
        if isinstance(v, str):
            d[k] = v.replace(old_str, new_str)
    return d


# Define a function that takes a file name and an API key as arguments and processes the file
def process_file(city, api_key, city_number):
    
    print(f'\nProcess: {city_number}, City: {city}')
    
    # getting attractions from list
    file = Path(f'{CHILDREN_ATTRACTIONS_LIST_DIR}/{city}.json')
    with open(file, 'r') as json_file:
        content = json.load(json_file)
    
    # getting a list of unique attractions  
    attractions = list(set(functools.reduce(lambda a, b: a + b, content.values())))
    print('\n', attractions)
    
    # getting all prompts and replace [city] tag with input city name    
    prompts = recursive_replace(get_prompts_GPT(PROMPTS_DIR/'children_attractions_pmt.json'), '[city]', city)

    # generation attractions' descriptions
    data = dict()
    for attraction in attractions:
        data[attraction] = json.loads(get_response_GPT(prompts['SEO'].replace('[attraction]', attraction), api_key))
        
    # write result in json
    SEO_CHILDREN_ATTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)  
    with open(f'{SEO_CHILDREN_ATTRACTIONS_DIR}/{city}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
            
    print(f'{city} processed successfully!')


def run_processes(key_numbers):
    # Get the list of input files
    cities = get_cities()

    # Get the list of API keys
    api_keys = [f'OPENAI_API_KEY_CT_{i + 3}' for i in range(key_numbers)]
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


if __name__ == '__main__':
    start = perf_counter()
    run_processes(1)
    hours = (perf_counter() - start) // 3600
    remained_seconds = (perf_counter() - start) % 3600 
    print(f'\nTime elapsed: {hours} h {remained_seconds // 60} min.\n')
