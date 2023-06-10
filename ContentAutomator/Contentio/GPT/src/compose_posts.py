from pathlib import Path
import json
import shutil
import traceback

from functions import get_cities, elapsed_time
from config import SMM_DIR, IMG_DIR, POSTS_DIR
     

missing_images = dict()
count = 0

def compose_posts(cities: list, option_name: str, option_number: str, 
                  texts_dir: Path | str, images_dir: Path | str, posts_dir: Path | str) -> None:
    # j = 0
    global count
    for city in cities:
        city = city.replace(' ', '_').replace('-', '_')
        try:
            image = next(Path(images_dir/city).glob(f'{option_number}_*.jpg'))
            count += 1
            # destination = Path(f'{posts_dir}/{option_name}_{option_number}/post_{j}')
            destination = Path(f'{posts_dir}/post_{count}')
            destination.mkdir(parents=True, exist_ok=True)
            with open(f'{texts_dir}/{city}.json', 'r') as f:
                texts = json.load(f)                                 
            with open(f'{destination}/text_ru.json', 'w', encoding='utf-8') as f:
                json.dump(texts[option_number], f, indent=4, ensure_ascii=False)
            shutil.copyfile(image, Path(f'{destination}/image.jpg'))
        except StopIteration as err:
            print(f'\nDuring {city} processing there was an error: {err.value}')
            if city not in missing_images.keys(): missing_images[city] = list()
            missing_images[city].append(option_number)
            continue
        except KeyError as err:
            print(err.args[0], city)
            exception_traceback = traceback.format_exc()
            print("Full Exception Description:")
            print(exception_traceback)
            
                   
@elapsed_time
def main():
    texts_dir = SMM_DIR/'city_attractions_first_person_ru'
    images_dir = IMG_DIR/'city_attractions'
    posts_dir = POSTS_DIR/'city_attractions_ru_'
    option_name = 'attraction'
    number_of_options = 10
    cities = get_cities()
    for i in range(1, number_of_options + 1):
        compose_posts(cities, option_name, str(i), texts_dir, images_dir, posts_dir)
    with open('missing_images.json', 'w') as f:
        json.dump(missing_images, f, sort_keys=True, indent=4)    


if __name__ == '__main__':
    main()
    
