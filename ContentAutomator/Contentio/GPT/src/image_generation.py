import requests
import os
import json
import openai

from functions import get_response_GPT, get_prompts_GPT, get_images_DALLE

from config import SEO_CHILDREN_ATTRACTIONS_DIR, PROMPTS_DIR


def download_image(url: str, city: str, anum: str, attraction: str, num: int) -> None:
    save_directory = f'../cities_data/images/children_attractions/{city}/{anum} {attraction}'
    image_name = f'{num}.jpeg'
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
        

def generate_image():
    api_key = 'OPENAI_API_KEY_CT_2'
    prompts = get_prompts_GPT(PROMPTS_DIR/'children_attractions_images_pmt.json')
    json_files = [file for file in os.listdir(SEO_CHILDREN_ATTRACTIONS_DIR) if file.endswith('.json')]
    for json_file in sorted(json_files)[1:]:
        city = json_file.partition('.')[0]
        json_path = os.path.join(SEO_CHILDREN_ATTRACTIONS_DIR, json_file)
        with open(json_path, 'r') as file:
            content = json.load(file)
        for key, value in content.items():
            for attraction, data in value.items():
                summarised = get_response_GPT(prompts['summarise'].format(text=data['description']), api_key)
                created_images = get_images_DALLE(summarised, 5, '512x512', api_key)
                for i, image_url in enumerate(created_images, start=1):
                    download_image(image_url, city, key, attraction, i)


if __name__ == '__main__':
    generate_image()
    ...
