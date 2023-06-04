from datetime import datetime
from aiogram import types

from ContentAutomator.Postify.utils.TelegramBot.config import config
from ContentAutomator.Postify.utils.TelegramBot.loader import bot
from ContentAutomator.Postify.utils.methods import add_task


async def add_task_telegram(message: types.Message,
                            photo_path: str,
                            post_text: str,
                            post_date: datetime):
    async def post_telegram_immediate(photo_path, post_text):
        post = await bot.send_photo(chat_id=config.channel_id.get_secret_value(), photo=types.FSInputFile(photo_path))
        await bot.send_message(chat_id=config.channel_id.get_secret_value(), text=post_text,
                               reply_to_message_id=post.message_id)
        await message.answer(f'Successfully published on Telegram')

    await add_task(photo_path, post_text, task=post_telegram_immediate, post_date=post_date, trigger='date',
                   message=message)
    await message.answer(f'Post Planned for {post_date.strftime("%m/%d/%Y, %H:%M:%S")} on Telegram')
