from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
admin_id = config.admin_id
group_id = config.group_id
time_stamp = config.time_stamp
bot_name = config.bot_name
present = config.present
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
