from pathlib import Path
import json
import traceback


from functions import get_cities, elapsed_time, get_city_id
from config import POSTS_DIR, SMM_CITY_ATTRACTIONS_FP_DIR, CITY_ATTRACTIONS_IMG_DIR
     

posts_dir = Path(f'{POSTS_DIR}/city_attractions/ru')
base_url = 'http://20.240.63.21/files/images/city_attractions'


def get_posts(city: str) -> dict:
    print('get_posts starting...')
    with open(f'{SMM_CITY_ATTRACTIONS_FP_DIR}/{city}.json', 'r') as f:
        return json.load(f)


def get_images(city: str) -> list:
    print('get_images starting...')
    return Path(f'{CITY_ATTRACTIONS_IMG_DIR}/{city}').glob('[0-9]*.jpg')


def post_to_json(count: int, data: dict, city_id: int) -> None:
    post_number = city_id * 100 + count
    with open(f'{posts_dir}/{post_number}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def compose_post(city: str, images: list, posts: dict) -> None:
    print('compose starting...')
    for image in images:
        try:
            option_number = image.name.split('_')[0]        
            url = f'{base_url}/{city}/{image.name}'
            # remove hashtags and links from the text
            paragraphs = posts[option_number]['text'].split('\n\n')
            for paragraph in posts[option_number]['text'].split('\n\n'):
                if '#' in paragraph or 'http' in paragraph:
                    paragraphs.remove(paragraph)
            posts[option_number]['text'] = '\n\n'.join(paragraphs)
            # make hashtags as a list if aren't
            if not isinstance(posts[option_number]['hashtags'], list):
                posts[option_number]['hashtags'] = posts[option_number]['hashtags'].split(" ")
            # add a list of images' urls    
            posts[option_number]['images'] = list()
            posts[option_number]['images'].append(url)                                
        except KeyError as err:
            print(err.args[0], city)
            print(f'Full Exception Description: {traceback.format_exc()}')
            continue
    return posts
            
                      
@elapsed_time
def main():
    posts_dir.mkdir(parents=True, exist_ok=True)
    for city in get_cities():
        city_id = get_city_id(city)
        city = city.replace(' ', '_').replace('-', '_')
        posts = compose_post(city, get_images(city), get_posts(city))
        for key, post in posts.items():
            post_to_json(int(key), post, city_id)
          
                
                
if __name__ == '__main__':
    main()
    
