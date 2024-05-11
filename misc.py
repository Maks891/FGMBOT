import asyncio, sqlite3
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, types

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, loop=loop)
conn = sqlite3.connect("db.db")
cursor = conn.cursor()
