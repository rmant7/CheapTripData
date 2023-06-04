from datetime import datetime, timedelta
import facebook
import requests
from aiogram import types

from ContentAutomator.Postify.utils.methods import add_task


async def add_task_facebook(message: types.Message,
                            photo_path: str,
                            post_text: str,
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
                await message.answer(f'Failed to schedule the post. (planned) Response:\n{response.json()}')
                return False
        except Exception as e:
            await message.answer(f'Failed to schedule the post. (planned) Error\n{e}')
            raise e

    if post_date <= datetime.now():
        await message.answer('Post date is in the past.')
        return False
    elif post_date <= datetime.now() + timedelta(minutes=10):
        await add_task(acc_token, photo_path, post_text, page_name, task=post_facebook_immediate, post_date=post_date,
                       trigger='date', message=message)
        await message.answer(f'Post Planned for {post_date.strftime("%m/%d/%Y, %H:%M:%S")} on Facebook. (immediate)')
    else:
        await post_facebook_planned(acc_token, photo_path, post_text, page_name)
        await message.answer(f'Post Planned for {post_date.strftime("%m/%d/%Y, %H:%M:%S")} on Facebook. (planned)')
