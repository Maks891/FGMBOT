import time
from datetime import datetime, timedelta
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from commands.db import url_name, getstatus, get_name
from commands.admin.db import *
from commands.main import geturl
from commands.main import win_luser
import config as cfg
from commands.admin.loger import new_log
from bot import bot

async def mute_cmd(message):
   name1 = message.from_user.get_mention(as_html=True)
   if not message.reply_to_message:
      await message.reply("ℹ | Эта команда должна быть ответом на сообщение!")
      return
   try:
      muteint = int(message.text.split()[1])
      mutetype = message.text.split()[2]
      comment = " ".join(message.text.split()[3:])
   except IndexError:
      await message.reply('ℹ | Не хватает аргументов!\nПример:\n<code>/мут 1 ч причина</code>')
      return
   if mutetype == "ч" or mutetype == "часов" or mutetype == "час":
      dt = datetime.now() + timedelta(hours=muteint)
      timestamp = dt.timestamp()
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date = timestamp)
      await message.reply(f'👤 Администратор: {name1}\n🛑 Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n[⏰] Срок: {muteint} {mutetype}\n[📃]  Причина: {comment}',  parse_mode='html')
   if mutetype == "м" or mutetype == "минут" or mutetype == "минуты":
      dt = datetime.now() + timedelta(minutes=muteint)
      timestamp = dt.timestamp()
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date = timestamp)
      await message.reply(f'👤 Администратор: {name1}\n🛑 Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n[⏰] Срок: {muteint} {mutetype}\n[📃] Причина: {comment}',  parse_mode='html')
   if mutetype == "д" or mutetype == "дней" or mutetype == "день":
      dt = datetime.now() + timedelta(days=muteint)
      timestamp = dt.timestamp()
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date = timestamp)
      await message.reply(f'👤 Администратор: {name1}\n🛑 Замутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n[⏰] Срок: {muteint} {mutetype}\n[📃] Причина: {comment}',  parse_mode='html')

async def unmute_cmd(message):
   name1 = message.from_user.get_mention(as_html=True)
   if not message.reply_to_message:
      await message.reply("ℹ Эта команда должна быть ответом на сообщение!")
      return
   await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(True, True, True, True))
   await message.reply(f'👤  Администратор: {name1}\n[🔊] Размутил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>',  parse_mode='html')

async def ban_cmd(message):
   name1 = message.from_user.get_mention(as_html=True)
   if not message.reply_to_message:
      await message.reply("ℹ Эта команда должна быть ответом на сообщение!")
      return
   comment = " ".join(message.text.split()[1:])
   await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False))
   await message.reply(f'👤 Администратор: {name1}\n[🛑] Забанил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>\n[⏰] Срок: навсегда\n[📃] Причина: {comment}',  parse_mode='html')

async def unban_cmd(message):
   name1 = message.from_user.get_mention(as_html=True)
   if not message.reply_to_message:
      await message.reply("ℹ Эта команда должна быть ответом на сообщение!")
      return
   await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(True, True, True, True))
   await message.reply(f'👤 Администратор: {name1}\n[📲] Разбанил: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>',  parse_mode='html')


async def ping(message: types.Message):
    a = time.time()
    bot_msg = await message.answer(f'⚙ Проверка пинга....')
    if bot_msg:
        b = time.time()
        await bot_msg.edit_text(f'🏓 Пинг: {round((b - a) * 1000)} ms')

def reg(dp: Dispatcher):
    dp.register_message_handler(mute_cmd, commands=['mute', 'мут'], commands_prefix='!?./', is_chat_admin=True)
    dp.register_message_handler(unmute_cmd, commands=['unmute', 'размут'], commands_prefix='!?./', is_chat_admin=True)
    dp.register_message_handler(ban_cmd, commands=['ban', 'бан', 'кик', 'kick'], commands_prefix='!?./', is_chat_admin=True)
    dp.register_message_handler(unban_cmd, commands=['разбан', 'unban'], commands_prefix='!?./', is_chat_admin=True)
    dp.register_message_handler(ping, commands=['ping', 'пинг'], commands_prefix='!?./')
