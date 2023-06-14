# 1. get option list
# 2. if option not in texts then generate missed text
# 3. if option not in image list then generate missed image
# 4. Recompose the posts


import requests
import json
from PIL import Image
from io import BytesIO
from pathlib import Path
from functions import get_cities, get_prompts_GPT, get_images_DALLE, get_response_GPT
from config import SMM_CITY_ATTRACTIONS_FP_DIR, CITY_ATTRACTIONS_IMG_DIR, CITY_ATTRACTIONS_LIST_DIR
from config import PROMPTS_DIR


def get_options(city: str) -> dict:
    with open(f'{CITY_ATTRACTIONS_LIST_DIR}/{city}.json', 'r') as f:
        return json.load(f)


def get_texts(city: str) -> dict:
    with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'r') as f:
        return json.load(f)
    

def get_images_list(city: str) -> set:
    return {file.name.split('_')[0] 
            for file in Path(f'{CITY_ATTRACTIONS_IMG_DIR}/{city}').glob('*.jpg') if file.name[0].isdigit()}


def download_image(url: str, number: int, attraction: str, city: str) -> None:
    save_dir = Path(f'{CITY_ATTRACTIONS_IMG_DIR}/{city}')
    save_dir.mkdir(parents=True, exist_ok=True)
    image_name = f'{number}_{attraction.replace(" ", "_")}.jpg'
    save_path = Path(save_dir/image_name)
    try:
        response = requests.get(url)
        # Open the downloaded image using PIL
        with Image.open(BytesIO(response.content)) as image:
            # define the desired size and save
            new_size = (1024, 1024)
            resized_image = image.resize(new_size)
            resized_image.save(save_path, format='JPEG')
            print(f"\nImage saved to {save_path}")
    except IOError:
        print(f"\nUnable to download, open, or process the image from URL: {url}")
        

def main():
    text_prompts = get_prompts_GPT(f'{PROMPTS_DIR}/smm_city_attractions_fp_pmt_ru.json')
    image_prompt = f'Landscape view of {{}} in {{}}'
    for city in get_cities():
        city = city.replace(' ', '_').replace('-', '_')
        options, texts, image_numbers = get_options(city), get_texts(city), get_images_list(city)
        diff_text_numbers = set(options.keys()).difference(set(texts.keys()))
        diff_image_numbers = set(options.keys()).difference(image_numbers)
        for number in diff_image_numbers:
            print('\n', city, diff_text_numbers, diff_image_numbers)
            attraction = options[number]
            urls = get_images_DALLE(image_prompt.format(attraction, city))
            if not urls: continue
            for url in urls:
                download_image(url, number, attraction, city)
        for number in diff_text_numbers:
            print('\n', city, diff_text_numbers, diff_image_numbers)
            attraction = options[number]
            prompt = text_prompts['prompt_ru'].format(option=attraction, city=city)
            texts[number] = get_response_GPT(prompt)
        with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'w', encoding='utf-8') as f:            
            json.dump(texts, f, indent=4, ensure_ascii=False)
        
        # if all([diff_texts, diff_images]):
        #     print(city, diff_texts, diff_images)
    
    
if __name__ == '__main__':
    main()
    # print(get_options_list('Rome'))
    # print(get_texts_list('Rome'))
    # print(get_images_list('Rome'))