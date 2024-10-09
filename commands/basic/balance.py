from datetime import datetime
from aiogram import Dispatcher, types
from commands.db import getstatus, getbalance, getads, getpofildb, url_name, chek_user
from assets.antispam import antispam, new_earning_msg, antispam_earning
from assets.transform import transform as trt
from assets.transform import transform_int as tr
from commands.basic.property import lists
from assets import kb
from bot import bot


@antispam
async def balance_cmd(message):
    name, balance, btc, bank, yen = await getbalance(message.from_user.id)
    ads = await getads()

    await message.answer(f'''👫 Ник: {name}
💰 Деньги: {tr(balance)}$
💴 Йены: {tr(yen)}¥
🏦 Банк: {tr(bank)}$
💽 Биткоины: {tr(btc)}🌐

{ads}''', disable_web_page_preview=True)


@antispam
async def btc_cmd(message):
    name, _, btc, _, _ = await getbalance(message.from_user.id)
    await message.answer(f'{name}, на вашем балансе {tr(btc)} BTC 🌐', disable_web_page_preview=True)


async def creat_help_msg(user_id, profil):
    status = await getstatus(user_id)
    url = await url_name(user_id)
    profil = profil.format(url)

    data, _, _ = await getpofildb(user_id)

    status_dict = {0: "Обычный", 1: "Standart VIP", 2: "Gold VIP", 3: "Platinum VIP", 4: "Администратор"}
    st = status_dict.get(status, status_dict[0])
    dregister = datetime.fromtimestamp(data[6]).strftime('%Y-%m-%d в %H:%M:%S')

    text = f'''{profil}
🪪 ID: {data[21]}
🏆 Статус: {st}
💰 Денег: {trt(data[2])}$
💴 Йены: {trt(data[22])}¥
🏦 В банке: {trt(data[4])}$
💳 B-Coins: {trt(data[15])}
💽 Биткоины: {trt(data[3])}฿
🏋 Энергия: {data[8]}
👑 Рейтинг: {trt(data[13])}
🌟 Опыт: {tr(data[7])}
🎲 Всего сыграно игр: {tr(data[14])}

<blockquote>📅 Дата регистрации:\n{dregister}</blockquote>'''
    return text


@antispam
async def profil_cmd(message):
    user_id = message.from_user.id
    msg = message.text

    profil = '{0}, ваш профиль:'

    if len(msg.split()) >= 2:
        status = await getstatus(user_id)
        try:
            user_id = int(msg.split()[1])
            if status != 4:
                await message.answer(f'❌ Вы не администратор чтобы просматривать профили.')
                return

            if not (await chek_user(user_id)):
                await message.answer(f'❌ Данного игрока не существует. Перепроверьте указанный <b>Telegram ID</b>')
                return

            profil = 'Профиль игрока {0}:'
        except:
            pass

    text = await creat_help_msg(user_id, profil)
    msg = await message.answer(text, reply_markup=kb.profil(user_id))
    await new_earning_msg(msg.chat.id, msg.message_id)


@antispam_earning
async def profil_busines(call: types.CallbackQuery):
    _, business, _ = await getpofildb(call.from_user.id)

    txt = ''
    if business[0]: txt += '\n  🔋 Ферма: Майнинг ферма'
    if business[1]: txt += '\n  💼 Бизнес: Бизнес'
    if business[2]: txt += '\n  🌳 Сад: Сад'
    if business[3]: txt += '\n  ⛏ Генератор: Генератор'
    if txt == '': txt = '\n🥲 У вас нету бизнесов'

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'🧳 Ваши бизнесы:{txt}', reply_markup=kb.profil_back(call.from_user.id))


@antispam_earning
async def profil_property(call: types.CallbackQuery):
    _, _, data = await getpofildb(call.from_user.id)

    txt = ''
    if data[4]:
        name = lists.phones.get(data[4])
        txt += f'\n  📱 Телефон: {name[0]}'

    if data[2]:
        name = lists.cars.get(data[2])
        txt += f'\n  🚘 Машина: {name[0]}'

    if data[1]:
        name = lists.helicopters.get(data[1])
        txt += f'\n  🚁 Вертолёт: {name[0]}'

    if data[6]:
        name = lists.planes.get(data[6])
        txt += f'\n  🛩 Самолёт: {name[0]}'

    if data[3]:
        name = lists.yahts.get(data[3])
        txt += f'\n  🛥 Яхта: {name[0]}'

    if data[5]:
        name = lists.house.get(data[5])
        txt += f'\n  🏠 Дом: {name[0]}'

    if txt == '': txt = '\n🥲 У вас нету имущества'

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'📦 Ваше имущество:{txt}', reply_markup=kb.profil_back(call.from_user.id))


@antispam_earning
async def profil_back(call: types.CallbackQuery):
    text = await creat_help_msg(call.from_user.id, '{0}, ваш профиль:')
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=text, reply_markup=kb.profil(call.from_user.id))


def reg(dp: Dispatcher):
    dp.register_message_handler(balance_cmd, lambda message: message.text in ['б', 'Б', 'Баланс', 'баланс'])
    dp.register_message_handler(btc_cmd, lambda message: message.text in ['биткоины', 'Биткоины'])
    dp.register_message_handler(profil_cmd, lambda message: message.text.lower().startswith('профиль'))
    dp.register_callback_query_handler(profil_busines, text_startswith='profil-busines')
    dp.register_callback_query_handler(profil_back, text_startswith='profil-back')
    dp.register_callback_query_handler(profil_property, text_startswith='profil-property')
