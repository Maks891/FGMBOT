from aiogram import Bot, Dispatcher, types
from commands.db import reg_user
from assets import kb
import random
import config as cfg


async def on_start(message):
    await reg_user(message.from_user.id)
    sticker_id = 'CAACAgQAAxkBAAEKs6JlSQUtGTtSzXGVcJGBe0PwnWkI9QACRwkAAm0NeFIe5FE9nk15XTME'
    await message.answer_sticker(sticker=sticker_id)

    await message.answer(f'''🤖 Добро пожаловать на борт, Кто-то! Меня зовут FGM, твой верный игровой бот.

🎮 У меня есть множество интересных команд и игр, чтобы скрасить твоё время, будь ты один или в компании друзей! (Кстати, вместе всегда веселее) 💙
🔍 Познакомиться со всеми моими возможностями ты можешь, введя команду «помощь».

<a href="https://t.me/FGMINFO">🔈 Наш канал</a>
<a href="https://t.me/FGMOFF">💬 Наш чат</a>''', disable_web_page_preview=True, reply_markup=kb.start())

    await message.answer(f'''🚀 Не уверен, с чего начать своё приключение?
Присоединяйся к нашему официальному чату FGM: https://t.me/FGMOFF''', disable_web_page_preview=True)


async def win_luser():
    win = ['🙂', '😋', '😄', '🤑', '😃', '😇']
    loser = ['😔', '😕', '😣', '😞', '😢']
    rwin = random.choice(win)
    rloser = random.choice(loser)
    return rwin, rloser


async def yznat_cmd(message: types.Message):
    if message.reply_to_message:
        mentioned_user_id = message.reply_to_message.from_user.id
        await message.answer(f"ID человека: {mentioned_user_id}")
    else:
        await message.answer("Сообщение пользователя не было отмечено.")

async def geturl(id, txt):
    url = f'<a href="tg://user?id={id}">{txt}</a>'
    return url
