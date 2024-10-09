from aiogram import Dispatcher, types
from commands.db import url_name, get_balance, getads
from decimal import Decimal
from assets.antispam import antispam
from commands.main import win_luser
from commands.basic.ore import db
import commands.basic.ore.dig
from assets.transform import transform_int as tr


@antispam
async def sellbtc(message: types.Message):
    user_id = message.from_user.id
    btc = await db.getbtc(user_id)
    url = await url_name(user_id)
    win, lose = await win_luser()

    try:
        summ_btc = int(message.text.split()[2])
    except:
        summ_btc = btc
    summ_btc = Decimal(summ_btc)
    btc = Decimal(btc)

    kurs = await db.getkurs()
    summ = summ_btc * kurs

    if btc >= summ_btc:
        if btc - summ_btc >= 0 and summ_btc > 0:
            await db.sellbtc_db(summ, summ_btc, user_id)
            await message.answer(f'{url}, вы успешно продали {tr(summ_btc)} BTC за {tr(summ)}$ {win}')
        else:
            await message.answer(f'{url}, нельзя продавать отрицательно или же нулевое количество BTC {lose}')
    else:
        await message.answer(f'{url}, вы не можете продать столько BTC {lose}')


@antispam
async def buybtc(message: types.Message):
    user_id = message.from_user.id
    balance = await get_balance(user_id)
    url = await url_name(user_id)
    win, lose = await win_luser()

    try:
        summ_btc = int(message.text.split()[2])
    except:
        await message.answer(f'{url}, вы не ввели количество BTC которое хотите купить {lose}')
        return

    summ_btc = Decimal(summ_btc)

    kurs = await db.getkurs()
    summ = summ_btc * kurs

    if balance >= summ:
        if summ_btc > 0:
            await db.buybtc_db(summ, summ_btc, user_id)
            await message.answer(f'{url}, вы успешно купили {tr(summ_btc)} BTC за {tr(summ)}$ {win}')
        else:
            await message.answer(f'{url}, нельзя покупать отрицательно или же нулевое количество BTC {lose}')
    else:
        await message.answer(f'{url}, у вас недостаточно денег для покупки BTC {lose}')


@antispam
async def btc_kurs(message: types.Message):
    user_id = message.from_user.id
    url = await url_name(user_id)
    kurs = await db.getkurs()
    ads = await getads(message)
    await message.answer(f'{url}, на данный момент курс 1 BTC составляет - {tr(kurs)}$ 🌐\n\n{ads}', disable_web_page_preview=True)


@antispam
async def rrating_cmd(message: types.Message):
    user_id = message.from_user.id
    url = await url_name(user_id)
    r = await db.getrrating(message)
    await message.answer(f'''{url}, ваш рейтинг {tr(r)}👑''', disable_web_page_preview=True)


@antispam
async def sellrating(message: types.Message):
    user_id = message.from_user.id
    r = await db.getrrating(message)
    url = await url_name(user_id)
    win, lose = await win_luser()

    try:
        summ_r = int(message.text.split()[2])
    except:
        summ_r = r

    summ_r = Decimal(summ_r)

    kurs = 100_000_000  # сумма за 1 рейтинг
    summ = summ_r * kurs

    if r >= summ_r:
        if r - summ_r >= 0 and summ_r > 0:
            await db.sellrrating_db(summ, summ_r, user_id)
            await message.answer(f'{url}, вы понизили количество вашего рейтинга на {tr(summ_r)}👑 за {tr(summ)}$ {win}')
        else:
            await message.answer(f'{url}, вы неправильно ввели число рейтинга которое хотите продать {lose}')
    else:
        await message.answer(f'{url}, у вас недостаточно рейтинга для его продажи {lose}')


@antispam
async def buy_ratting(message: types.Message):
    user_id = message.from_user.id
    balance = await get_balance(user_id)
    url = await url_name(user_id)
    win, lose = await win_luser()

    try:
        r_summ = int(message.text.split()[1])
    except:
        await message.answer(f'{url},  вы неправильно ввели число рейтинга которое хотите купить {lose}')
        return

    r_summ = Decimal(r_summ)
    kurs = 150_000_000  # стоимость 1 рейтинга
    summ = r_summ * kurs

    if balance >= summ:
        if r_summ > 0:
            await db.buyratting_db(summ, r_summ, user_id)
            await message.answer(f'{url}, вы повысили количество вашего рейтинга на {tr(r_summ)}👑 за {tr(summ)}$ {win}')
        else:
            await message.answer(f'{url}, вы неправильно ввели число рейтинга которое хотите купить {lose}')
    else:
        await message.answer(f'{url}, у вас недостаточно денег для покупки рейтинга {lose}')


def reg(dp: Dispatcher):
    dp.register_message_handler(sellbtc, lambda message: message.text.lower().startswith('продать биткоин'))
    dp.register_message_handler(buybtc, lambda message: message.text.lower().startswith('купить биткоин'))
    dp.register_message_handler(btc_kurs, lambda message: message.text.lower().startswith('курс биткоина'))
    dp.register_message_handler(rrating_cmd, lambda message: message.text.lower() == 'рейтинг')
    dp.register_message_handler(buy_ratting, lambda message: message.text.lower().startswith('рейтинг'))
    dp.register_message_handler(sellrating, lambda message: message.text.lower().startswith('продать рейтинг'))

    commands.basic.ore.dig.reg(dp)
