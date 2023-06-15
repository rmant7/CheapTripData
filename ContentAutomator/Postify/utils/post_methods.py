import asyncio
import logging
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
import facebook
import requests
from aiogram import types

from utils.config import config
from utils.loader import bot
from utils.methods import add_task, record_post_info, get_post_data, get_page, check_if_post_exists


async def add_task_facebook(post_path: str,
                            post_date: datetime,
                            page_name: str,
                            acc_token: str):
    async def post_facebook_immediate(acc_token: str, images: list, post_text: str, page_name: str):
        try:
            # Set name of the pages where we want to post
            page = get_page(acc_token, page_name)
            graphPage = facebook.GraphAPI(page['access_token'])
            # Upload the image
            for image in images:
                graphPage.put_photo(image=image, album_path='me/photos', message=post_text)
        except Exception as e:
            logging.warning(f'Error in post_facebook_immediate \n{e}')
            raise e

    async def post_facebook_planned(acc_token: str, images: list, post_text: str, page_name: str):
        ACC_ACCESS_TOKEN = acc_token
        try:
            # The Facebook ID of the page to post on
            page = get_page(acc_token, page_name)

            GET_TOKEN_URL = f'https://graph.facebook.com/{page["id"]}?fields=access_token&access_token={ACC_ACCESS_TOKEN}'

            # The page access token from Facebook App
            PAGE_ACCESS_TOKEN = requests.get(url=GET_TOKEN_URL).json()['access_token']

            # Scheduled time in the future
            SCHEDULED_TIME = int(post_date.timestamp())

            # The Graph API endpoint for photos
            url = f'https://graph.facebook.com/{page["id"]}/photos'

            # The image to post
            image_data_list = []
            for index, image in enumerate(images):
                image_data = {
                    f'file{index}': image
                }
                image_data_list.append(image_data)
            files = {k: v for d in image_data_list for k, v in d.items()}

            # The other parameters
            post_data = {
                'access_token': PAGE_ACCESS_TOKEN,
                'published': 'false',
                'scheduled_publish_time': SCHEDULED_TIME,
                'message': post_text
            }

            # Send the POST request
            response = requests.post(url, data=post_data, files=files)
            logging.warning(response.json())
            # Print the response
            if response.status_code == 200:
                return True
            else:
                logging.warning(f'Failed to schedule the post. (planned) Response:\n{response.json()}')
                return False
        except facebook.GraphAPIError:
            logging.warning('facebook.GraphAPIError\n Continue in 20 minutes')
            await asyncio.sleep(1200)
            await post_facebook_planned(acc_token, images, post_text, page_name)
        except Exception as e:
            logging.warning(f'Failed to schedule the post. (planned) Error\n{e}')
            raise e
            # return False

    social = 'Facebook'
    if not check_if_post_exists(path=post_path, social=social):
        logging.warning(f'{post_path} post already exists')
        return False

    post_text, images = await get_post_data(post_path)

    if post_date <= datetime.now():
        logging.warning('Post date is in the past.')
        return False
    elif post_date <= datetime.now() + timedelta(minutes=10):
        await add_task(acc_token, images, post_text, page_name, task=post_facebook_immediate, post_date=post_date,
                       trigger='date')
        logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (immediate)\n')
        record_post_info(path=post_path, social=social)
        return True
    else:
        await post_facebook_planned(acc_token, images, post_text, page_name)
        logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (planned)\n')
        record_post_info(path=post_path, social=social)
        return True


async def add_task_telegram(post_path: str, post_date: datetime):
    async def post_telegram_immediate(image_urls: [str], post_text: str):
        image_urls = [
            "http://20.240.63.21/files/images/city_attractions/Tehran/1_Golestan_Palace.jpg",
            "http://20.240.63.21/files/images/city_attractions/Tehran/2_National_Museum_of_Iran.jpg",
            "http://20.240.63.21/files/images/city_attractions/Tehran/3_Tehran_Bazaar.jpg"
        ]
        media = [types.InputMediaPhoto(media=url) for url in image_urls]
        post = await bot.send_media_group(chat_id=config.channel_id.get_secret_value(), media=media)
        await bot.send_message(chat_id=config.channel_id.get_secret_value(), text=post_text,
                               reply_to_message_id=post.message_id)

    social = 'Telegram'
    if not check_if_post_exists(path=post_path, social=social):
        logging.warning(f'{post_path} post already exists')
        return False

    post_text, image = await get_post_data(post_path)

    await add_task(image, post_text, task=post_telegram_immediate, post_date=post_date, trigger='date')
    logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (immediate)\n')
    record_post_info(path=post_path, social=social)
    return True
