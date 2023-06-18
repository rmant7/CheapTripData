import pandas as pd
import json
from time import perf_counter
from pathlib import Path

from functions import get_response_GPT, get_prompts_GPT, elapsed_time, is_valid_link
from config import PROMPTS_DIR, SEO_CITY_DESCRIPTIONS_DIR, IMG_DIR


@elapsed_time
def complete_seo_description():
    prompts_dir = Path(f'{PROMPTS_DIR}/city_descriptions_pmt.json')
    img_dir = Path(f'{IMG_DIR}/city_descriptions')
    base_url = 'http://20.240.63.21/files/images/city_descriptions'
    missing = {'cities':[]}
    # with open('missing_cities.json', 'r') as f:
    #     missing_cities = json.load(f)
    for json_ in SEO_CITY_DESCRIPTIONS_DIR.glob('*.json'):
        with open(json_, 'r') as f:
            json_content = json.load(f)
        prompts = get_prompts_GPT(prompts_dir)
        try:
            response = json.loads(get_response_GPT(prompts['city_description'].format(description=json_content['description'])))
            for k, v in response.items(): json_content[k] = v
            if not is_valid_link(json_content['link']): json_content['link'] = ''
            json_content['images'] = [f'{base_url}/{json_.stem}/{image.name}' 
                                      for image in list(Path(f'{img_dir}/{json_.stem}').glob("*.jpg"))]
            with open(json_, 'w') as f:
                json.dump(json_content, f, indent=4)
        except Exception as err:
            print('\nSomething went wrong: ', err)
            missing['cities'].append(json_.stem)
            continue
    with open('missing_cities', 'w') as f:
        json.dump(missing, f, indent=4)
        
    
if __name__ == '__main__':
    complete_seo_description()