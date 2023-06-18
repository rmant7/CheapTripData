from pathlib import Path
import json
from datetime import datetime


from logger import logger_setup
from functions import get_cities, elapsed_time, get_city_id
from config import POSTS_DIR, SMM_CITY_ATTRACTIONS_FP_DIR, CITY_ATTRACTIONS_IMG_DIR
     

posts_dir = Path(f'{POSTS_DIR}/city_attractions/ru')
base_url = 'http://20.240.63.21/files/images/city_attractions'
logger = logger_setup(Path(__file__).stem)


def get_texts(city: str) -> dict:
    logger.info(f'getting texts...')
    file_path = f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json'
    try:
        with open(file_path, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError as err:
        logger.error(err)


def get_images(city: str) -> list:
    logger.info(f'getting images...')
    folder_path = f'{CITY_ATTRACTIONS_IMG_DIR}/{city}'
    try:
        images = list(Path(folder_path).glob('[0-9]*.jpg'))
        if not images: raise FileNotFoundError(images)
        return images
    except FileNotFoundError as err:
        logger.error(f'No images were found: {err}')


def post_to_json(count: int, data: dict, city_id: int) -> None:
    post_number = city_id * 100 + count
    file_path = f'{posts_dir}/{post_number}.json'
    try:
        with open(file_path, 'w', encoding='utf-8') as fp:
            logger.info(f'posting data to: {post_number}.json')
            json.dump(data, fp, indent=4, ensure_ascii=False)
    except FileNotFoundError as err:
        logger.error(f'Disable posting to {file_path} because of error: {err}')


missing = dict()
def compose_post(city: str, images: list, texts: dict) -> None:
    if not texts or not images: return None
    logger.info(f'composing posts...')
    for image in images:        
        url = f'{base_url}/{city}/{image.name}'
        index = image.name.split('_')[0]
        try:
            # find hashtags and links in the 'text' and remove them
            paragraphs = texts[index]['text'].split('\n\n')
            for paragraph in texts[index]['text'].split('\n\n'):
                if '#' in paragraph or 'http' in paragraph:
                    paragraphs.remove(paragraph)
            texts[index]['text'] = '\n\n'.join(paragraphs)
            # make hashtags as a list if aren't
            if not isinstance(texts[index]['hashtags'], list):
                texts[index]['hashtags'] = texts[index]['hashtags'].split(" ")
            # add a list of images' urls    
            texts[index]['images'] = list()
            texts[index]['images'].append(url)                                
        except KeyError as err:
            logger.error(err)
            continue
        except TypeError as err:
            logger.error(err)
            continue
    return {k:v for k, v in texts.items() if 'images' in v.keys()}
           
                      
@elapsed_time
def main():
    posts_dir.mkdir(parents=True, exist_ok=True)
    cities = get_cities()
    j = 0
    for city in cities:
        city_id = get_city_id(city)
        logger.info(f'starting...{city.upper()} {city_id}')
        city = city.replace(' ', '_').replace('-', '_')
        try:
            posts = compose_post(city, get_images(city), get_texts(city))
            for key, post in posts.items():
                post_to_json(int(key), post, city_id)
        except AttributeError as err:
            logger.error(f'No posts for {city} {city_id} were composed because of error: {err}')
            continue
        logger.info(f'completed successfully...{city.upper()} {city_id}, total processed: {j + 1}/{len(cities)}')
        j += 1        

                
if __name__ == '__main__':
    main()