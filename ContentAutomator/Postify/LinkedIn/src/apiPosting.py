import json
import requests
from pathlib import Path
import random
import sys
from datetime import datetime
import re

from logger import logger_setup
from env import ACCESS_TOKEN, ID_COMPANY, TARGET_URL, DEFAULT_POST_FOLDER, FILES_FOLDER, CONSTANT_HASHTAGS


timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = logger_setup(f'{Path(__file__).stem}')


def remove_non_alphanumeric(raw: str) -> str:
    invalid_symbols = r'[^a-zA-Z0-9äöüÄÖÜßàáâãäåæçèéêëìíîïðòóôõöøùúûüýÿ]'
    return re.sub(invalid_symbols, '', raw)


def get_request_data(request_data_path: str) -> tuple:
    try:
        with open(Path(request_data_path), 'r') as f:
            request_data = json.load(f)
            
        return request_data['api_url'], request_data['headers'], request_data['request_body']
    
    except FileNotFoundError as err:
        file_path = Path(err.filename)
        logger.critical(f'Input file: "../{file_path.parent.name}/{file_path.name}" is not found')
        
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
        

def choice_post_to_share(post_folder: str) -> Path:
    try:
        post_folder = Path(post_folder)
        posted_path = Path(f'{FILES_FOLDER}/linkedin_posted.json')
        with open(posted_path, 'r') as f:
            posted = json.load(f)
        
        json_ids = set(v.stem for v in post_folder.glob('*.json'))
        random_json_id = random.choice(list(json_ids.difference(posted['posted'])))
        to_post_path = next(post_folder.glob(f'{random_json_id}.json'))
        
        return to_post_path
    
    except FileNotFoundError as err:
        if err.filename == str(posted_path):
            with open(posted_path, 'w') as f:
                json.dump({'posted':[]}, f, indent=4)
            logger.warning(f'File "{posted_path.parent.name}/{posted_path.name}" was created from scratch')
        
            return choice_post_to_share(post_folder)
        
        logger.error(f'{type(err).__name__}: {err.filename}')   
                
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')


def get_post_content(file_path: Path) -> dict:
    try:
        with open(file_path, 'r') as f:
            post_content=json.load(f)
            
        return post_content
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def prepare_text_to_share(name: str, location: str, title: str, text: str, hashtags: list) -> str:
    try:
        city, country = location.split(', ')
        name, city, country = map(remove_non_alphanumeric, (name, city, country))
                
        hashtags_top = f'#{name} #{city} #{country}'    
        hashtags_bottom = CONSTANT_HASHTAGS + ' ' + ' '.join(hashtags)
    
        text_to_share = f'{hashtags_top}\n\n{title}\n\n{text}\n\nFind out more at {TARGET_URL}\n\n{hashtags_bottom}\n'
        
        return text_to_share
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def register_image() -> tuple():
    try:
        api_url, headers, request_body = get_request_data(f'{FILES_FOLDER}/schema_request_register_image.json')
        
        # insert credentials into request body
        headers['Authorization'] = headers['Authorization'].format(access_token = ACCESS_TOKEN)
        request_body['registerUploadRequest']['owner'] = request_body['registerUploadRequest']['owner'].format(id_company = ID_COMPANY)
        
        response = requests.post(api_url, json=request_body, headers=headers)
        response.raise_for_status()
       
        data = json.loads(response.text)
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = data['value']['asset']
        
        return upload_url, asset
    
    except requests.HTTPError as err:
        logger.error(f'Post creation failed with status code: {response.status_code}')
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def upload_binary_image(image_path: str, upload_url: str) -> None:
    try:
        image_path = Path(image_path.replace(TARGET_URL, '/home/azureuser'))
        with open(image_path, 'rb') as f:
            binary_image = f.read()
                
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}', 
            'X-Restli-Protocol-Version': '2.0.0'
        }

        response = requests.post(upload_url, binary_image, headers=headers)
        response.raise_for_status()
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def share_text_and_image(text_to_share: str, asset: str) -> str:
    try:
        api_url, headers, request_body = get_request_data(f'{FILES_FOLDER}/schema_request_text_image_share.json')
                
        # insert credentials into request body
        headers['Authorization'] = headers['Authorization'].format(access_token = ACCESS_TOKEN)
        request_body['author'] = request_body['author'].format(id_company = ID_COMPANY)
        
        # assign input values
        request_body['specificContent']['com.linkedin.ugc.ShareContent']['shareCommentary']['text'] = text_to_share
        request_body['specificContent']['com.linkedin.ugc.ShareContent']['media'][0]['media'] = asset

        response = requests.post(api_url, headers=headers, json=request_body)
        response.raise_for_status()
        
        if response.status_code == 201:
            return 'Post from {from_} about {about_} in {in_} is shared SUCCESFULLY'
            
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}') 


def add_to_posted(post_id: str) -> None:
    try:
        posted_path = Path(f'{FILES_FOLDER}/linkedin_posted.json')
        with open(posted_path, 'r') as f:
            posted = json.load(f)
            
        posted['posted'].append(post_id)
        
        with open(posted_path, 'w') as f:
            json.dump(posted, f, indent=4)
            
    except FileNotFoundError as err:
        file_path = Path(err.filename)
        logger.critical(f'Input file: "../{file_path.parent.name}/{file_path.name}" not found')
        
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}') 


def main(lang: str='en'):
    # choice *.json from the posts folder en/ (by default)
    post_folder = f'{DEFAULT_POST_FOLDER}/{lang}'
    post_to_share = choice_post_to_share(post_folder)
    
    # get content of choiced json
    post_content = get_post_content(post_to_share)
    
    # from json content compile name, location, title, text, hashtags into the one object
    text_data = {k: v for k, v in post_content.items() if k not in ('links', 'images')}
    text_to_share = prepare_text_to_share(**text_data)
    
    # request to register image and ...
    upload_url, asset = register_image()
    
    # ... then upload binary image file ...in order to ...
    image_path = post_content['images'][0]
    upload_binary_image(image_path, upload_url)
    
    # ... share both the text and the image
    result = share_text_and_image(text_to_share, asset)
    logger.info(result.format(from_=post_to_share.name, about_=text_data['name'], in_=text_data['location']))
    
    # add file name in posted file
    add_to_posted(post_to_share.stem)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print(f'Usage: python3 {Path(__file__).name} [ru]')
        sys.exit(1)
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()