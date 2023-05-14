import multiprocessing
import json
from pathlib import Path
from time import perf_counter
import functools

from config import CHILDREN_ATTRACTIONS_LIST_DIR, SEO_CHILDREN_ATTRACTIONS_DIR


def process_file():
    files = sorted(list(Path(f'{CHILDREN_ATTRACTIONS_LIST_DIR}').glob('*.json')))
    for file in files:  
        # getting json content
        with open(file, 'r') as json_list:
            attrlist = json.load(json_list)
        
        with open(f'{SEO_CHILDREN_ATTRACTIONS_DIR}_3/{file.name}', 'r') as json_desc:
            attrdesc = json.load(json_desc)
            
        # # getting a list of unique attractions  
        # attractions = sorted(list(set(functools.reduce(lambda a, b: a + b, content.values()))))
        # print('\n', attractions)
        
        data = dict()
        for key, value in attrlist.items():
            if value in attrdesc.keys():
                data[key] = dict()
                data[key][value] = attrdesc[value]
        
        # write result in json
        SEO_CHILDREN_ATTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)  
        with open(f'{SEO_CHILDREN_ATTRACTIONS_DIR}/{file.name}', 'w') as json_file:
            json.dump(data, json_file, indent=4) 
                        
        print(f'{file.name} processed successfully!')


if __name__ == '__main__':
    start = perf_counter()
    process_file()
    hours = (perf_counter() - start) // 3600
    remained_seconds = (perf_counter() - start) % 3600 
    print(f'\nTime elapsed: {hours} h {remained_seconds // 60} min.\n')
