import asyncio
import logging
from datetime import datetime, timedelta
import facebook
import requests
from aiogram import types

from ContentAutomator.Postify.utils.methods import add_task, get_post_data, record_post_info


async def add_task_facebook(post_path: str,
                            post_date: datetime,
                            page_name: str,
                            acc_token: str):
    # Get account page by name
    def get_page(acc_token, page_name):
        # Set the graph with access_token_for_user
        graph = facebook.GraphAPI(acc_token)
        # Get the list of pages managed by you
        accounts = graph.get_connections('me', 'accounts')
        page = None
        for account in accounts['data']:
            if account['name'] == page_name:
                page = account
        return page

    async def post_facebook_immediate(acc_token: str, photo_path: str, post_text: str, page_name: str):
        # Set name of the pages where we want to post
        page = get_page(acc_token, page_name)
        graphPage = facebook.GraphAPI(page['access_token'])

        # Upload the image
        with open(photo_path, 'rb') as image_file:
            image_data = image_file.read()
            graphPage.put_photo(image=image_data, album_path='me/photos', message=post_text)

    async def post_facebook_planned(acc_token: str, photo_path: str, post_text: str, page_name: str):
        ACC_ACCESS_TOKEN = acc_token
        try:
            # The Facebook ID of the page to post on
            page = get_page(acc_token, page_name)

            GET_TOKEN_URL = f'https://graph.facebook.com/{page["id"]}?fields=access_token&access_token={ACC_ACCESS_TOKEN}'

            # The page access token from Facebook App
            PAGE_ACCESS_TOKEN = requests.get(url=GET_TOKEN_URL).json()['access_token']

            # The image path
            IMAGE_PATH = photo_path

            # Scheduled time in the future
            SCHEDULED_TIME = int(post_date.timestamp())

            # The Graph API endpoint for photos
            url = f'https://graph.facebook.com/{page["id"]}/photos'

            # The image to post
            image_data = {
                'file': open(IMAGE_PATH, 'rb')
            }

            # The other parameters
            post_data = {
                'access_token': PAGE_ACCESS_TOKEN,
                'published': 'false',
                'scheduled_publish_time': SCHEDULED_TIME,
                'message': post_text
            }

            # Send the POST request
            response = requests.post(url, data=post_data, files=image_data)
            # Print the response
            if response.status_code == 200:
                return True
            else:
                logging.warning(f'Failed to schedule the post. (planned) Response:\n{response.json()}')
                return False
        except facebook.GraphAPIError:
            logging.warning('facebook.GraphAPIError\n Continue in 20 minutes')
            await asyncio.sleep(1200)
            await post_facebook_planned(acc_token, photo_path, post_text, page_name)
        except Exception as e:
            logging.warning(f'Failed to schedule the post. (planned) Error\n{e}')
            raise e

    social = 'Facebook'
    if not record_post_info(path=post_path, social=social):
        logging.warning(f'{post_path} post already exists')
        return False

    post_text, photo_path = await get_post_data(post_path)

    if post_date <= datetime.now():
        logging.warning('Post date is in the past.')
        return False
    elif post_date <= datetime.now() + timedelta(minutes=10):
        await add_task(acc_token, photo_path, post_text, page_name, task=post_facebook_immediate, post_date=post_date,
                       trigger='date')
        logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (immediate)\n')
        return True
    else:
        await post_facebook_planned(acc_token, photo_path, post_text, page_name)
        logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (planned)\n')
        return True
