import asyncio
import json
import logging
import os
import aioschedule
from aiogram import types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ContentAutomator.Postify.utils.TelegramBot.config import config
from ContentAutomator.Postify.utils.TelegramBot.loader import bot


async def add_task(*args, task, post_date, trigger='date', message=None):
    scheduler = AsyncIOScheduler()

    try:
        scheduler.add_job(task, args=args, trigger=trigger, run_date=post_date)
        scheduler.start()
        return True
    except Exception as e:
        raise e


async def get_post_data(path):
    try:
        with open(f'{path}/text.json', 'r') as f:
            data = json.load(f)
            locationsList = data['location'].split(',')
            locations = ''
            for item in locationsList:
                word = item.split(' ')
                locations = locations + ' #'
                for subItem in word:
                    locations = locations + subItem.capitalize()
            hashtags = ''
            footer = """
Find out more at https://cheaptrip.guru\n
#CheapTripGuru #travel #cheaptrip #budgettravel
"""
            for hashtag in data['hashtags']:
                hashtags = hashtags + hashtag + ' '

            text = locations.replace("'", '') + '\n' + data['text'] + '\n' + footer + '\n' + hashtags
            photo = types.FSInputFile(f'{path}/image.jpg')
            await asyncio.sleep(5)
            message = await bot.send_photo(chat_id=config.channel_id.get_secret_value(), photo=photo)
            await bot.send_message(chat_id=config.channel_id.get_secret_value(), text=text,
                                   reply_to_message_id=message.message_id)
            print(f"{locations} successfully published")

    except Exception as e:
        logging.warning(f'Error. {e}, \n {path}')


async def iterate_folder(path='files'):
    for item in os.listdir(path):
        new_path = path + '/' + item
        if os.path.isdir(new_path):
            await iterate_folder(new_path)
        else:
            post_path = path + '/'
            await get_post_data(post_path)
            break


async def clear_tasks():
    aioschedule.clear()
