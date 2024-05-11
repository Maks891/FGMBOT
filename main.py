from aiogram import executor, types
from misc import dp, bot, conn, cursor
from config import logchat

from aiogram.types import Message, ChatType
from aiogram.utils.markdown import quote_html
from asyncio import sleep

@dp.message_handler(commands=['start'], chat_type = ChatType.PRIVATE)
async def cmd_start(message: types.Message):
    user = message.from_user
    status = await get_user(message)
    if status is None:
        cursor.execute(f"INSERT INTO users VALUES (?, ?)", (user.id, 0))
        conn.commit()
        await message.reply("Можешь написать любой текст, задать вопрос.")
    elif status[1] == 1:
        await message.reply("Вы заблокированы!")
    else:
        await message.reply("Можешь написать любой текст, задать вопрос.")

@dp.message_handler(content_types=["text"], chat_type = ChatType.PRIVATE)
async def main(message: types.Message):
    try:
        user = message.from_user
        chat = message.chat
        fullname = quote_html(user.full_name)
        if message.text.startswith("/"):
            return
        if message.text.lower():
            status = await get_user(message)
            if status[1] == 0:
                await message.reply("Сообщение доставлено!\nОжидайте ответа.")
                await bot.send_message(logchat, f"#{user.id} Новое сообщение!\n"
                                                f"Имя: <a href='tg://user?id={user.id}'>{fullname}</a> | ID: <code>{user.id}</code>\n\n"
                                                f"{message.text}")
            elif status[1] == 1:
                await message.reply("Вы заблокированы!")
    except: return await message.reply(f"Обнови бота\n/start")

@dp.message_handler(commands=['answer'])
async def cmd_answer(message: types.Message):
    chat = message.chat
    reply = message.reply_to_message
    if reply:
        args = message.get_args()
        if args:
            if chat.id == logchat:
                data = reply.text.split("#")[1].split()[0]
                user = await bot.get_chat(int(data))
                await bot.send_message(user.id, f"Вам ответили!\n\n{args}")
                await sleep(2)
                await bot.delete_message(logchat, reply.message_id)
                await bot.delete_message(logchat, message.message_id)

@dp.message_handler(commands=['block'])
async def cmd_block(message: types.Message):
    chat = message.chat
    reply = message.reply_to_message
    if reply:
        if chat.id == logchat:
            data = reply.text.split("#")[1].split()[0]
            user = await bot.get_chat(int(data))
            cursor.execute(f'UPDATE users SET status=? WHERE user_id=?', (1, user.id,))
            conn.commit()
            await bot.send_message(user.id, f"Вас заблокировали!")
            await sleep(2)
            await bot.delete_message(logchat, reply.message_id)
            await bot.delete_message(logchat, message.message_id)

@dp.message_handler(commands=['unblock'])
async def cmd_unblock(message: types.Message):
    chat = message.chat
    args = message.get_args()
    if args:
        if chat.id == logchat:
            user = await bot.get_chat(int(args))
            fullname = quote_html(user.full_name)
            cursor.execute(f'UPDATE users SET status=? WHERE user_id=?', (0, user.id,))
            conn.commit()
            await message.reply(f"Вы разблокировали {fullname}.")
            await bot.send_message(user.id, f"Вас разблокировали!")

@dp.message_handler(commands=['blocked'])
async def cmd_blocked(message: types.Message):
    chat = message.chat
    if chat.id == logchat:
        users = await get_blocked(message)
        await message.reply(f"Заблокированные пользователи.\n\n{users}")

@dp.message_handler(commands=['users'])
async def cmd_users(message: types.Message):
    chat = message.chat
    if chat.id == logchat:
        users = await get_users(message)
        await message.reply(f"Всего <b>{users}</b> пользователей в базе данных бота!")

async def get_user(message: types.Message):
    user = message.from_user
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    return data

async def get_users(message: types.Message):
    users = cursor.execute("SELECT user_id FROM users").fetchall()
    allusers = len(users)
    return allusers

async def get_blocked(message: types.Message):
    blocked = cursor.execute("SELECT user_id FROM users WHERE status=?", (1,)).fetchall()
    allblocked = ""
    for x in blocked:
        user = await bot.get_chat(int(x[0]))
        allblocked += f"• {user.first_name} | ID: <code>{user.id}</code>\n"
    return allblocked

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
