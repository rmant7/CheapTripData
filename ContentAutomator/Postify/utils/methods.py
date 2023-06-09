import json
import logging
import os
import aioschedule
import facebook
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ContentAutomator.Postify.utils.TelegramBot.config import config
from ContentAutomator.Postify.utils.TelegramBot.loader import bot


async def add_task(*args, task, post_date, trigger='date'):
    scheduler = AsyncIOScheduler()

    try:
        scheduler.add_job(task, args=args, trigger=trigger, run_date=post_date)
        scheduler.start()
        return True
    except Exception as e:
        raise e


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


# reads files from the path, structures them. Returns the text and photo ready for publication
async def get_post_data(path: str):
    try:
        with open(f'{path}/text.json', 'r') as f:
            data = json.load(f)
            # make hashtags from locations
            locationsList = data['location'].split(',')
            locations = ''
            for item in locationsList:
                # replaces symbols in hashtags
                item = item.replace("'", ' ')
                item = item.replace("-", ' ')
                item = item.replace("&", ' ')
                word = item.split(' ')
                locations = locations + ' #'
                for subItem in word:
                    locations = locations + subItem.capitalize()

            hashtags = ''
            footer = """
Find out more at \nhttps://cheaptrip.guru\n
#CheapTripGuru #travel #cheaptrip #budgettravel
"""
            for hashtag in data['hashtags']:
                hashtags = hashtags + hashtag + ' '

            #   makes a ready post
            text = locations + '\n' + data['text'] + '\n' + footer + '\n' + hashtags
            photo = f'{path}/image.jpg'
            # photo = types.FSInputFile(f'{path}/image.jpg')

            if text and photo:
                return text, photo

    except Exception as e:
        logging.warning(f'Error. {e}, \n {path}')


# iterates over folders and return paths with data
async def get_data_directory(all_paths: dict, path: str):
    for element in os.listdir(path):
        new_path = path + '/' + element
        # if the element is a folder, we go deeper
        if os.path.isdir(new_path):
            await get_data_directory(all_paths=all_paths, path=new_path)
        # else if the element is a file, we save path to the file and repeating the loop
        else:
            if element not in ['text.json', 'image.jpg']:
                break

            post_path = path + '/'
            all_paths[post_path] = {}
            break
    return all_paths


def record_post_info(path, social):
    with open('ContentAutomator/Postify/posts_info.json', 'r') as json_file:
        try:
            posts = json.load(json_file)
        except:
            posts = {}

        if path not in posts:
            posts[path] = []
        elif social in posts[path]:
            return False

        posts[path].append(social)
        with open('ContentAutomator/Postify/posts_info.json', 'w') as output_json:
            output_json.write(json.dumps(posts, indent=4))
        return True


def get_scheduled_tasks(acc_token: str, page_name: str):
    page = get_page(acc_token, page_name)

    page_id = page['id']
    access_token = page['access_token']

    url = f"https://graph.facebook.com/v17.0/{page_id}/scheduled_posts"

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # print(json.dumps(response.json(), indent=4))
        posts = response.json()
        for post in posts['data']:
            print(post)
        return posts

    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.json())


async def clear_tasks():
    aioschedule.clear()
