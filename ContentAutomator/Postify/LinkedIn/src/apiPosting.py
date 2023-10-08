import json
import requests
from pathlib import Path
import random
import sys
from datetime import datetime

from logger import logger_setup
from env import ACCESS_TOKEN, ID_COMPANY, TARGET_URL, DEFAULT_POST_FOLDER, CONSTANT_HASHTAGS


timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logger = logger_setup(f'{Path(__file__).stem}')
# logger = logger_setup(f'{Path(__file__).stem}_{timestamp}')


def get_request_data(request_data_path: str) -> tuple:
    try:
        with open(Path(request_data_path), 'r') as f:
            request_data = json.load(f)
        return request_data['api_url'], request_data['headers'], request_data['request_body']
    except Exception as err:
        print(f'{type(err).__name__:} {err}')
        

def get_post_to_share(post_folder: str) -> Path:
    try:
        post_folder = Path(post_folder)
        
        posted_path = Path('../files/linkedin_posted.json')
        with open(posted_path, 'r') as f:
            posted = json.load(f)
        
        json_ids = set(v.stem for v in post_folder.glob('*.json'))
        random_json_id = random.choice(list(json_ids.difference(posted['posted'])))
        to_post_path = next(post_folder.glob(f'{random_json_id}.json'))
        logger.info(f'Post to share: {to_post_path.name}')
        
        return to_post_path
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')


def get_post_content(file_path: Path) -> dict:
    try:
        with open(file_path, 'r') as f:
            post_content=json.load(f)
            logger.info(f'Post content extracted from: {file_path.name}')
        return post_content
    except Exception as err:
        print(f'{type(err).__name__:} {err}')
    
    
def prepare_text_to_share(data: dict) -> str:
    try:
        hashtags_top = f'#{"".join(data["name"].split())} '\
                    f'#{"".join(data["location"].split(", ")[0])} '\
                    f'#{"".join(data["location"].split(", ")[1])}'    
        
        title = data['title']
        text = data['text']
        hashtags_bottom = CONSTANT_HASHTAGS + ' ' + ' '.join(data['hashtags'])
    
        text_to_share = f'{hashtags_top}\n\n{title}\n\n{text}\n\nFind out more at {TARGET_URL}\n\n{hashtags_bottom}\n'
        
        logger.info(f'Text to share is prepared: {data["name"]} in {data["location"]}')
        
        return text_to_share
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def register_image() -> tuple():
    try:
        api_url, headers, request_body = get_request_data('../files/schema_request_register_image.json')
        logger.info(f'Request schema is parsed')
        
        # insert credentials
        headers['Authorization'] = headers['Authorization'].format(access_token = ACCESS_TOKEN)
        request_body['registerUploadRequest']['owner'] = request_body['registerUploadRequest']['owner'].format(id_company = ID_COMPANY)
        logger.info(f'Credentials are added into the request body')
        
        logger.info(f'POST request is started')
        response = requests.post(api_url, json=request_body, headers=headers)
        response.raise_for_status()
        logger.info(f'Response received with a status code: {response.status_code}')
       
        data = json.loads(response.text)
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = data['value']['asset']
        logger.info(f'Upload Url and asset are parsed')
        
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
        logger.info(f'The binary mode image is obtained: {image_path.name}')
        
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}', 
            'X-Restli-Protocol-Version': '2.0.0'
        }

        logger.info(f'POST request is started')
        response = requests.post(upload_url, binary_image, headers=headers)
        response.raise_for_status()
        logger.info(f'Response received with a status code: {response.status_code}')
    
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}')
    
    
def share_text_and_image(text_to_share: str, asset: str) -> None:
    try:
        api_url, headers, request_body = get_request_data('../files/schema_request_text_image_share.json')
        logger.info(f'Request schema is parsed')
        
        # insert credentials
        headers['Authorization'] = headers['Authorization'].format(access_token = ACCESS_TOKEN)
        request_body['author'] = request_body['author'].format(id_company = ID_COMPANY)
        logger.info(f'Credentials are added into the request body')
        
        # assign input values
        request_body['specificContent']['com.linkedin.ugc.ShareContent']['shareCommentary']['text'] = text_to_share
        request_body['specificContent']['com.linkedin.ugc.ShareContent']['media'][0]['media'] = asset
        logger.info(f'Text to share and asset are added into the request body')

        logger.info(f'POST request is started')
        response = requests.post(api_url, headers=headers, json=request_body)
        response.raise_for_status()
        if response.status_code == 201:
            logger.info('Post successfully created!')
            # print('Post successfully created!')
            
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}') 


def add_to_posted(file_path: Path) -> None:
    try:
        posted_path = Path('../files/linkedin_posted.json')
        
        with open(posted_path, 'r') as f:
            posted = json.load(f)
            
        posted['posted'].append(file_path.stem)
        
        with open(posted_path, 'w') as f:
            json.dump(posted, f, indent=4)

        logger.info(f'File {file_path.name} is added to posted files list')
        
    except Exception as err:
        logger.error(f'{type(err).__name__}: {err}') 


def main(lang: str='en'):
    # choice *.json from the posts folder en/ by default
    post_folder = f'{DEFAULT_POST_FOLDER}/{lang}'
    logger.info(f'Posting process is started with source: {post_folder}')
    post_to_share = get_post_to_share(post_folder)
    
    # get content of choiced json
    post_content = get_post_content(post_to_share)
    
    # from json content compile name, location, title, text, hashtags into the one object
    text_data = {k: v for k, v in post_content.items() if k not in ('links', 'images')}
    text_to_share = prepare_text_to_share(text_data)
    
    # get image url and make requests to register image and ...
    upload_url, asset = register_image()
    
    # ... then upload binary image file
    image_path = post_content['images'][0]
    upload_binary_image(image_path, upload_url)
    
    # share the text and the image
    share_text_and_image(text_to_share, asset)
    
    # add file name in posted file
    add_to_posted(post_to_share)
    
    logger.info(f'Posting process is finished successfully!')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print(f'Usage: python3 {Path(__file__).name} [ru]')
        sys.exit(1)
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
  