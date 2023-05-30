from pathlib import Path
import json
import shutil

from functions import get_cities
from config import CITY_ATTRACTIONS_IMG_DIR, CITY_ATTRACTIONS_LIST_DIR, SMM_CITY_ATTRACTIONS_FP_DIR, SMM_POSTS_DIR


def images_numbering():
    cities = get_cities()
    for city in cities:
        with open(f'{CITY_ATTRACTIONS_LIST_DIR}/{city}.json', 'r') as json_file:
            attractions = json.load(json_file)
        images = list(Path(CITY_ATTRACTIONS_IMG_DIR/city).glob('*.jpg'))
        for image in images:
            image_name = image.name.partition('.')[0]
            for number, attraction in attractions.items():
                if attraction == image_name:
                    image.rename(f'{image.parent}/{number}_{"_".join(image_name.split(" "))}.jpg')
                    print(image.name)


def json_restructuring():
    cities = get_cities()
    for city in cities:
        with open(f'{CITY_ATTRACTIONS_LIST_DIR}/{city}.json', 'r') as json_file:
            attractions = json.load(json_file)   
        with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'r') as json_file:
            content = json.load(json_file)
        data = dict()
        for key in content.keys():
            for number, attraction in attractions.items():
                if key == attraction:
                    data[number] = {'name':key, 'text':content[key]['text'], 'hashtags':content[key]['hashtags']} 
                    with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    break
            
    
def post_composition(attraction_number: str):
    cities = get_cities()
    j = 0
    for i, city in enumerate(cities, start=1):
        with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'r') as json_file:
            content = json.load(json_file)
        data = dict()
        try:
            data['location'] = f"{content[attraction_number]['name']}, {city}"
            data['text'] = content[attraction_number]['text']
            data['hashtags'] = content[attraction_number]['hashtags']
            j += 1
            destination = Path(f'{SMM_POSTS_DIR}/city_attractions_{attraction_number}/post_{j}')
            destination.mkdir(parents=True, exist_ok=True)
            with open(f'{destination}/text.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)
            images = list(Path(CITY_ATTRACTIONS_IMG_DIR/city).glob('*.jpg'))
            for image in images:
                image_name = image.name.partition('.')[0]
                if image_name.split('_')[0] == attraction_number:
                    shutil.copyfile(image, Path(f'{destination}/image.jpg'))
                    break
        except Exception as err:
            print(f'\nDuring {city} processing there was an error: {err}')
            continue
             

if __name__ == '__main__':
    # images_numbering()
    # json_restructuring()
    for i in range(1, 7):
        post_composition(str(i))
    
