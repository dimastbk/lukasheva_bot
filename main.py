import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import Throttled
from dotenv import load_dotenv

import db
from utils import parse_author

load_dotenv()
API_TOKEN = os.environ["API_TOKEN"]


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def update_result_message(chat_id: int):
    result_list = await db.get_result_list()

    text = "*Результаты:*"
    for idx, item in enumerate(result_list):
        text += f"\n{idx + 1:> 2}. {item[0]} - {item[1]}"

    settings = await db.get_settings()
    if settings:
        await bot.edit_message_text(text, chat_id, settings[1], parse_mode=types.ParseMode.MARKDOWN)
    else:
        message = await bot.send_message(chat_id, text=text, parse_mode=types.ParseMode.MARKDOWN)
        await message.pin(disable_notification=True)
        await db.update_settings(chat_id, message.message_id)


def get_like_button(count: int | None = None):
    text = f"❤️ {count}" if count else "❤️"
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text, callback_data="like"))


async def throttled(query: types.CallbackQuery, *args, **kwargs):
    await query.answer("Не лайкайте слишком часто :)", show_alert=True)


@dp.callback_query_handler(text="like")
@dp.throttled(throttled, rate=1)
async def callback(query: types.CallbackQuery):
    await query.answer()

    await db.update_log(query.message.message_id, query.from_user.id, parse_author(query.message.md_text))
    count = await db.get_count(query.message.message_id)

    await query.message.edit_reply_markup(get_like_button(count))

    await update_result_message(query.message.chat.id)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def read_photo(message: types.Message):

    text = f"Автор: [{message.from_user.full_name}](tg://user?id={message.from_user.id})"
    if message.caption:
        text += f"\nСообщение: {message.caption}"

    await bot.send_photo(
        message.chat.id,
        message.photo[0].file_id,
        caption=text,
        parse_mode=types.ParseMode.MARKDOWN,
        reply_markup=get_like_button(),
    )
    await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=db.create_all)
