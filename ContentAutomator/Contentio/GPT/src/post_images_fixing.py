import json, os, requests
from functions import get_images_DALLE
from config import CITY_ATTRACTIONS_LIST_DIR, CITY_ATTRACTIONS_IMG_DIR, SMM_POSTS_DIR


def download_image(url: str, city: str, anum: int, attraction: str) -> None:
    attraction = "_".join(attraction.split(" "))
    save_directory = f'{CITY_ATTRACTIONS_IMG_DIR}/{city}/'
    image_name = f'{anum}_{attraction}.jpg'
    save_path = os.path.join(save_directory, image_name)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image {image_name} downloaded and saved to: {save_path}")       
    except requests.exceptions.HTTPError as error:
        print(f"\nDuring file '{url}' processing there was an error: {error}")


def post_images_fix():
    source = '../cities_data/smm/errorPaths.txt'
    api_key = 'OPENAI_API_KEY_CT_2'
    image_size = '1024x1024'
    number_of_images = 1
    
    with open(source, 'r') as source_file:
        error_pathes = [path[:-1] for path in source_file.readlines()]
    
    cities = set()
    for path in error_pathes:
        with open(f'{SMM_POSTS_DIR}/{path}/text.json', 'r') as json_file:
            city = json.load(json_file)['location'].split(', ')[1]
            cities.add(city)
    
    for city in cities:
        if city == 'Fukuoka':
            with open(f'{CITY_ATTRACTIONS_LIST_DIR}/{city}.json', 'r') as json_file:
                attractions = json.load(json_file)
            print(city, list(attractions.values()), sep='\n')
            for anum, attraction in attractions.items():
                prompt = 'landscape view of {} in the city of {}'.format(attraction, city) 
                print('\n', prompt)  
                try:
                    created_images = get_images_DALLE(prompt, number_of_images, image_size, api_key)
                    for image_url in created_images:
                        download_image(image_url, city, anum, attraction)
                except Exception:
                    continue
    

if __name__ == '__main__':
    post_images_fix()