import multiprocessing
import json
from pathlib import Path
from time import perf_counter

from functions import get_prompts_GPT, get_response_GPT
from config import ATTRACTIONS_LIST_DIR, PROMPTS_DIR, SEO_CITY_ATTRACTIONS_DIR


def recursive_replace(d, old_str, new_str):
    for k, v in d.items():
        if isinstance(v, dict):
            recursive_replace(v, old_str, new_str)
        if isinstance(v, str):
            d[k] = v.replace(old_str, new_str)
    return d


# Define a function that takes a file name and an API key as arguments and processes the file
def process_file(file, api_key, file_number):
    
    city = file.name.partition('.')[0]
    print(f'\nProcess: {file_number}, City: {city}')
    
    # getting attractions from list
    with open(file, 'r') as json_file:
        attractions = json.load(json_file).values()
    
    prompts = recursive_replace(get_prompts_GPT(PROMPTS_DIR/'city_attractions_pmt.json'), '[city]', city)
    
    data = dict()
    for attraction in attractions:
        response = get_response_GPT(prompts['attraction'].replace('[attraction]', attraction), api_key)
        response = response.strip(' ').strip('\"')
        response = response.replace('Title: ', '').replace('\n\n', '\n')
        data[attraction] = dict()
        data[attraction]['text'] = response
        data[attraction]['summary'] = get_response_GPT(prompts['summary'].replace('[text]', response), api_key)
        data[attraction]['keywords'] = get_response_GPT(prompts['keywords'].replace('[text]', response), api_key).strip(' ').split(', ')
    
    # write result in json
    SEO_CITY_ATTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)  
    with open(f'{SEO_CITY_ATTRACTIONS_DIR}/{city}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
            
    print(f'{city} processed successfully!')


def run_processes(key_numbers=1):
    # Get the list of input files
    files = sorted(list(Path(ATTRACTIONS_LIST_DIR).glob('*.json')))

    # Get the list of API keys
    api_keys = [f'OPENAI_API_KEY_CT_{i}' for i in range(key_numbers)]

    # Create a pool of processes with as many workers as there are API keys
    pool = multiprocessing.Pool(len(api_keys))

    # Loop through the files and create a thread for each one
    for i, file in enumerate(files):
        # Get the corresponding API key by cycling through the list
        api_key = api_keys[i % len(api_keys)]
        # Create a thread object with the target function and the file name and API key as arguments
        pool.apply_async(process_file, args=(file, api_key, i + 1))
        
    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()


if __name__ == '__main__':
    start = perf_counter()
    run_processes()
    hours = (perf_counter() - start) // 3600
    remained_seconds = (perf_counter() - start) % 3600 
    print(f'\nTime elapsed: {hours} h {remained_seconds // 60} min.')
