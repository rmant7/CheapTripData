import json
import logging
import os
import aioschedule
import facebook
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from io import BytesIO
from bs4 import BeautifulSoup


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
        unicode_data = requests.get(path).json()
        decoded_data = json.dumps(unicode_data, indent=4, ensure_ascii=False)
        data = json.loads(decoded_data)
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
        for hashtag in hashtags:
            hashtags = hashtags + hashtag + ' '

        footer = "Больше о нас: \nhttps://cheaptrip.guru\n\n#CheapTripGuru #travel #cheaptrip #budgettravel"
        # footer = "Find out more at \nhttps://cheaptrip.guru\n\n#CheapTripGuru #travel #cheaptrip #budgettravel"

        #   makes a ready post
        text = locations + '\n' + data['text'] + '\n\n' + footer + '\n' + hashtags
        # print(text)

        images = []
        for image_url in data['images']:
            response = requests.get(image_url, stream=True)
            images.append(BytesIO(response.content))
        # photo = types.FSInputFile(f'{path}/image.jpg')

        if text and images:
            return text, images
    except Exception as e:
        raise e
        # logging.warning(f'Error. {e}, \n {path}')


# reads files from the url, structures them. Returns the text and photo ready for publication
async def get_post_data_new(url: str):
    try:
        unicode_data = requests.get(url).json()
        decoded_data = json.dumps(unicode_data, indent=4, ensure_ascii=False)
        data = json.loads(decoded_data)

        def get_hashtags():
            hashtags = ' '.join([hashtag for hashtag in data['hashtags']])
            name = '#' + ''.join([item.capitalize() for item in (data['name'].split(' '))])
            locations_list = [item.capitalize() for item in (data['location'].split(', '))]
            location = ' '.join([f'#{item}' for item in locations_list]) + name

            hashtags = f'{hashtags} {name} {location}'
            return location, hashtags

        footer = 'Больше о нас:\nhttps://cheaptrip.guru'

        location, hashtags = get_hashtags()

        text = location + '\n' + data["text"] + '\n\n' + footer + '\n\n' + hashtags
        images = []

        image_url_list = data['images']
        for image_url in image_url_list:
            response = requests.get(image_url, stream=True)
            images.append(BytesIO(response.content))

            return text, images
    except Exception as e:
        raise e
        # logging.warning(f'Error. {e}, \n {path}')


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
    with open('utils/posts_info.json', 'r') as json_file:
        try:
            posts = json.load(json_file)
        except:
            posts = {}

        if path not in posts:
            posts[path] = []
        elif social in posts[path]:
            return False

        posts[path].append(social)
        with open('utils/posts_info.json', 'w') as output_json:
            output_json.write(json.dumps(posts, indent=4))
        return True


def check_if_post_exists(path, social):
    with open('utils/posts_info.json', 'r') as json_file:
        try:
            posts = json.load(json_file)
        except:
            posts = {}

        if path not in posts:
            return True
        elif social in posts[path]:
            return False

        posts[path].append(social)
        with open('utils/posts_info.json', 'w') as output_json:
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

    def get_data(response_data):
        data = {}
        for item in response_data:
            data[item['id']] = {'created_time': item['created_time'].split('+')[0].replace('T', ', '),
                                'post': item['message'].split('\n')[0], 'id': item['id']}
        return data

    data = {}
    if response.status_code == 200:
        data.update(get_data(response.json()['data']))
        while 'next' in response.json()['paging']:
            response = requests.get(response.json()['paging']['next'], headers=headers)
            data.update(get_data(response.json()['data']))
        return data
    else:
        print(f"Request failed with status code {response.status_code}")


async def clear_tasks():
    aioschedule.clear()


async def get_names_from_link(url):
    try:
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        files = []
        for link in links:
            if '.json' in link.getText():
                files.append(link.getText())
        return files
    except Exception as e:
        logging.warning(f'Failed to parse files from the link. Error:\n{e}')
