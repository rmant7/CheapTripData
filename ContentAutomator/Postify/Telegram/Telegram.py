import logging
from datetime import datetime
from aiogram import types

from ContentAutomator.Postify.utils.TelegramBot.config import config
from ContentAutomator.Postify.utils.TelegramBot.loader import bot
from ContentAutomator.Postify.utils.methods import add_task, record_post_info, get_post_data


async def add_task_telegram(post_path: str,
                            post_date: datetime):
    async def post_telegram_immediate(photo_path, post_text):
        post = await bot.send_photo(chat_id=config.channel_id.get_secret_value(), photo=types.FSInputFile(photo_path))
        await bot.send_message(chat_id=config.channel_id.get_secret_value(), text=post_text,
                               reply_to_message_id=post.message_id)

    social = 'Telegram'
    if not record_post_info(path=post_path, social=social):
        return False

    post_text, photo_path = await get_post_data(post_path)

    await add_task(photo_path, post_text, task=post_telegram_immediate, post_date=post_date, trigger='date')
    logging.warning(f'{post_path}\n{post_date.strftime("%m/%d/%Y, %H:%M:%S")}\n{social} (immediate)\n')
    return True
