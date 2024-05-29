import random
import asyncio

import aiogram

from config import ADMINS
from functions_db import Users, Meetings, Messages
from key import join_to_meeting, admin_main_panel, control_panel_for_admin_member, main_panel, \
    control_panel_for_second_member, control_panel


def create_new_meetings(first_member):
    """
    Создает новую сделку
    :param first_member: user_id пользователя который создает сделку
    :return: словарь с id встрече и ссылка на встречу
    """
    user = Users().select_one(user_id=first_member)

    # Если юзер уже в сделке
    if (user.get('his_meeting') and user.get('his_meeting') != 'None'):
        print(user.get('his_meeting'))
        return False

    id_metting = ''.join(random.choices("asdadjandkjandjkabduqliqopdji113453467656867s1133oqjd", k=10))
    meeting_url = "https://t.me/Garant4ek_bot?start="+id_metting

    Meetings().insert(id_meeting=id_metting, first_member=first_member)

    Users().update_his_meeting(user_id=user.get('user_id'), id_metting=id_metting)

    return {"id_meeting": id_metting,
            "url_meeting" : meeting_url}


def is_member_in_meeting(id_meeting, member_id):
    """
    Есть ли юзер в сделке
    :param id_meeting: id сделки
    :param member_id: user_id юзера, которого хотим проверить
    :return: False - если нет. True - если есть
    """
    meeting = Meetings().select_one(id_meeting=id_meeting)

    if not (meeting.get('first_member') == member_id or meeting.get('second_member') == member_id or meeting.get('admin') == member_id):
        return False

    else:
        return True


async def remove_second_member(bot_obj, message, id_meeting):
    """
    Удаляет юзера с Сделки, меняет ему значения в базе данных
    :param id_metting: id Сделки
    :return: id юзера 2, которого удалили
    """
    meeting = Meetings().select_one(id_meeting=id_meeting)
    if Users().select_one(user_id=meeting.get('second_member')):
        Users().update_his_meeting(user_id=meeting.get('second_member'), id_metting=meeting.get('id_metting'))
    else:
        await message.answer("Второго пользователя нету в сделке")
        return

    Meetings().update_second_member(id_meeting=id_meeting, second_member=None)

    await bot_obj.send_message(meeting.get('second_member'), "Вы были удалены со Сделки", reply_markup=main_panel())
    await message.answer(f"Вы успешно удалили со Сделки\n\nСсылка для приглашения - {meeting.get('url_meeting')}",
                         reply_markup=control_panel())

    return meeting.get('second_member')

def write_down_message(id_meeting, message, member_id):
    """
    Записывает сообщения в базу данных
    :param id_meeting: id Сделки
    :param message: Сообщения, которое нужно записать (уже сделано)
    :param member_id: Пользователь который написал смс
    :return: ОШИБКА если это написал админ или кто-то другой
    """
    meeting = Meetings().select_one(id_meeting=id_meeting)
    if member_id == meeting.get('first_member'):
        Messages().insert(id_meeting=id_meeting, message=message, first_member=True)

    elif member_id == meeting.get('second_member'):
        Messages().insert(id_meeting=id_meeting, message=message, second_member=True)

    elif member_id == meeting.get('admin'):
        Messages().insert(id_meeting=id_meeting, message=message, admin=True)

    else:
        raise OverflowError
    return True

def is_user_in_db(user_id):
    """
    Проверяет есть ли юзер в дб, если нет - то добавляет
    :param user_id: id юзера в телеграм
    :return:
    """
    if Users().select_one(user_id):
        return True
    else:
        Users().insert(user_id=user_id)
        return False


def check_url_meeting(message):
    """
    Проверяет перешел ли юзер по ссылке на Сделку
    :param message: обект сообщения с телеграм
    :return:
    """
    data_of_start = str(message.text).split(' ')
    # Если юзер перешел по какой-те ссылке
    if len(data_of_start) == 2:
        id_meeting = data_of_start[1]
        meeting = Meetings().select_one(id_meeting=id_meeting)

        # Если сделка существует и нету второго учасника
        if (meeting and (not meeting.get('second_member') or meeting.get('second_member') != 'None')):

            user = Users().select_one(user_id=message.chat.id)

            Users().update_his_meeting(user_id=user.get('user_id'), id_metting=id_meeting)

            Meetings().update_second_member(id_meeting=id_meeting, second_member=user.get('user_id'))

            return {"status": True, "meeting": meeting}

    return {"status": False}

async def call_garanta_for_meeting(bot, message_obj, id_meeting):
    """
    Вызывает гаранта в Сделку
    :param bot: обект бота с тг
    :param message_obj: обект смс с тг
    :param id_meeting: id Сделки
    :return: True - если успешно вызвали. False - если не вызвали, так как он уже вызван
    """
    meeting = Meetings().select_one(id_meeting=id_meeting)

    if meeting.get('need_garant') == 1:
        await message_obj.answer("Вы уже вызвали ГАРАНТА, пожалуйста подождите, когда он присоединится к вам")
        return False

    Meetings().update_need_garant(id_meeting=id_meeting, need_garant=1)

    # Отправка учасникам смс
    second_member = Users().select_one(user_id=meeting.get('second_member'))

    if meeting.get('second_member') and (message_obj.chat.id == second_member.get('user_id')):
        await message_obj.answer('Вы успешно вызвали гаранта, пожалуйста подождите, когда он присоединится к вам')
        await bot.send_message(meeting.get('first_member'), "Учасник вызвал гаранта, пожалуйста дождитесь его")

    else:
        await message_obj.answer('Вы успешно вызвали гаранта, пожалуйста подождите, когда он присоединится к вам')
        if meeting.get('second_member') and meeting.get('second_member') != 'None':
            await bot.send_message(meeting.get('first_member'), "Учасник вызвал гаранта, пожалуйста дождитесь его")

    # Уведомляем админов
    for admin in ADMINS:
        await bot.send_message(admin, f"Сделка № {meeting.get('id_meeting')} <b>Вызвала гаранта</b>", parse_mode='html')

    return True
#__________________________________________________________________________#

async def send_error_to_join_admin_as_member(Admin_sector, message_obj):
    """
    Если админ пробует подключиться к Сделке как простой учасник, то возвращаем ошибку
    :param Admin_sector:
    :param message_obj:
    :return:
    """
    if message_obj.chat.id in ADMINS:
        await message_obj.answer(
            'Вы не можете присоединится к Сделке как учасник, так как вы АДМИН. Зайдите в сделку от лица админа -> нажмите "Текущие Сделки" -> "Присоединится"',
            reply_markup=admin_main_panel())
        await Admin_sector.box.set()
        return False

    else:
        return True

async def make_mailing_to_all(bot, message_obj):
    """
    Делает рассылку всем юзерам
    :param bot: обект бота с телеграм
    :param message_obj: обект message с телеграм
    :return:
    """
    await message_obj.answer(f'Рассылка начата! Сообщение:\n\n{message_obj.text}', reply_markup=admin_main_panel())

    users = Users().select_all()

    failed = 0

    for user in users:
        if user[1] == message_obj.chat.id:
            continue

        try:
            await bot.send_message(user[1], f"#Рассылка:\n{message_obj.text}")
        except aiogram.utils.exceptions.BotBlocked:
            failed += 1

    await message_obj.answer(f"Расссылка закончена! Не отправилось <b>{failed} из {len(users)}</b>", reply_markup=admin_main_panel(),parse_mode='html')


def get_statistics_bot():
    """
    Достает и формирует статистику бота
    :return: готовый текст с с формированным текстом
    """
    count_users_in_bot = len(Users().select_all())

    count_active_meetings = len(Meetings().select_all())
    count_active_meetings_that_need_garant = len(Meetings().select_WHERE_need_garant(1))
    count_active_meetings_that_DONT_need_garant = len(Meetings().select_WHERE_need_garant(0))

    count_written_messages = len(Messages().select_all())

    text = f"Всего пользователей - <b>{count_users_in_bot}</b>\n\n" \
           f"Количество активных Сделок - <b>{count_active_meetings}</b>\n" \
           f"Количество активных Сделок, которые вызвали ГАРАНТА - <b>{count_active_meetings_that_need_garant}</b>\n" \
           f"Количество активных Сделок, которые <b>не</b> вызвали ГАРАНТА - <b>{count_active_meetings_that_DONT_need_garant}</b>\n\n" \
           f"Количество записанных сообщений - <b>{count_written_messages}</b>"
    return text

async def send_list_of_meetings(message):
    """
    Достает и отправляет список активаных сделок
    :param message: обект message с телеграм
    :return: None
    """
    meetings = Meetings().select_all()

    if meetings:
        answer = "Список активных сделок"
    else:
        answer = "Нету активных сделок"

    await message.answer(answer)

    for meeting in meetings:
        await message.answer(f"Сделка № {meeting[1]}\n\nСоздатель Сделки - {meeting[2]}\nВторой учасник Сделки - {meeting[3]}", reply_markup=join_to_meeting(meeting[1]))


async def send_meetings_that_need_garant(message_obj):
    """
    Достает и отправляет список сделок, которые вызвали ГАРАНТА
    :param message: обект message с телеграм
    :return: None
    """
    meetings = Meetings().select_WHERE_need_garant(1)

    if meetings:
        answer = "Список сделок"
    else:
        answer = "Нету сделок, которые вызвали гаранта"

    await message_obj.answer(answer)

    for meeting in meetings:
        await message_obj.answer(f"Сделка № {meeting[1]}\n\nСоздатель Сделки - {meeting[2]}\nВторой учасник Сделки - {meeting[3]}", reply_markup=join_to_meeting(meeting[1]))


async def remove_meeting(bot_obj, data_call):
    """
    Удаляет Сделку с бд
    :param bot_obj: обект бота которого мы создаем через токен (файл main.py)
    :param data_call: обект CallbackQuery
    :return: None
    """
    id_meeting = data_call.data.split(":")[1]
    meeting = Meetings().select_one(id_meeting=id_meeting)

    if meeting:
        Meetings().delete(id_meeting=id_meeting)
        Messages().delete_all(id_meeting=id_meeting)
        await data_call.message.answer('Сделка успешно удалена', reply_markup=admin_main_panel())

    else:
        await data_call.message.answer('Такой Сделки не существует', reply_markup=admin_main_panel())

    await bot_obj.delete_message(data_call.message.chat.id, data_call.message.message_id)

    # Пишем учасникам сделки, что ее удалили. И обновляем им статусы
    text = "Ваша Сделка была удалена администратором"

    await bot_obj.send_message(meeting.get('first_member'), text, reply_markup=main_panel())
    Users().update_his_meeting(user_id=meeting.get('first_member'), id_metting=None)

    if meeting.get('second_member'):
        await bot_obj.send_message(meeting.get('second_member'), text, reply_markup=main_panel())
        Users().update_his_meeting(user_id=meeting.get('second_member'), id_metting=None)


async def join_to_meeting_admin(state_obj, Meeting_sector, data_call):
    """
    Присоединяет админа в Сделку
    :param data_call: обект CallbackQuery
    :return: None
    """

    id_meeting = data_call.data.split(":")[1]
    meeting = Meetings().select_one(id_meeting=id_meeting)
    Meetings().update_admin_member(id_meeting=id_meeting, admin_id=data_call.message.chat.id)

    await state_obj.update_data(id_meeting=meeting.get('id_meeting'), admin=data_call.message.chat.id, first_member=meeting.get('first_member'), second_member=meeting.get('second_member'),
                                url_meeting=meeting.get('url_meeting'))


    Users().update_his_meeting(user_id=data_call.message.chat.id, id_metting=id_meeting)

    await Meeting_sector.box.set()


    await data_call.message.answer(f"Вы присоединились к Сделке № {meeting.get('id_meeting')}", reply_markup=control_panel_for_admin_member())

async def logout_from_meeting(bot, state_obj, message_obj, Admin_sector, id_meeting):
    """
    Выходит со Сделки и возвращает в гланое меню
    :param state_obj: обект state в телеграм боте
    :param message_obj: обект message в телеграм боте
    :param Admin_sector: класс Admin_sector для состояний для адмна
    :param id_meeting: id Сделки с которой делаем выход
    :return: None
    """
    await state_obj.finish()

    meeting = Meetings().select_one(id_meeting=id_meeting)

    Users().update_his_meeting(user_id=message_obj.chat.id, id_metting=None)

    if message_obj.chat.id in ADMINS:
        Meetings().update_admin_member(id_meeting=id_meeting, admin_id=None)
        await Admin_sector.box.set()
        await message_obj.answer(f"Вы вышли со Сделке № {meeting.get('id_meeting')}", reply_markup=admin_main_panel())

    else:
        Meetings().update_second_member(id_meeting=id_meeting, second_member=None)
        await message_obj.answer("Вы вышли со Сделки\n\n<b>Главное меню</b>", reply_markup=main_panel(), parse_mode='html')
        await bot.send_message(meeting.get('first_member'), f"Другой учасник <b>вышел</b> со Сделки\n\nСсылка для приглашения - {meeting.get('url_meeting')}", reply_markup=control_panel(), parse_mode='html')


async def send_all_messages_of_meeting(id_meeting, message):
    """
    Отправляет все сообщения Сделки админу
    :param id_meeting: id Сделки
    :param message: Обект сообщения с тг
    :return: None
    """
    msg = Messages().select_all_msg_of_meeting(id_meeting=id_meeting)
    await message.answer("🔰 - СТАРТ ПЕРЕПИСКИ - 🔰")

    # Пишем все сообщения
    for m in msg:
        await message.answer(m[2])

    await message.answer("🛑 -КОНЕЦ ПЕРЕПИСКИ - 🛑")

async def end_meeting(bot_obj, message, data_meeting):
    """
    Заканчивает и удаляет Сделку и их сообщения. Меняет статусы для юзеров
    :param bot_obj: обект бота которого мы создаем через токен (файл main.py)
    :param message: Обект сообщения с тг
    :param data_meeting: Данные о Сделки
    :return: None
    """

    # Достаем данные
    id_meeting, first_member, second_member, admin_member = data_meeting['id_meeting'], data_meeting['first_member'], data_meeting['second_member'], data_meeting['admin']

    # Удаляем Сделку
    Meetings().delete(id_meeting)
    # Удаляем Сообзения Сделки
    Messages().delete_all(id_meeting=id_meeting)

    # Обновляет статусы
    if admin_member:
        Users().update_his_meeting(admin_member, None)

    Users().update_his_meeting(first_member, None)

    if second_member:
        Users().update_his_meeting(second_member, None)

    if message.chat.id == first_member:
        await message.answer("Сделка завершена", reply_markup=main_panel())

        if admin_member:
            await bot_obj.send_message(int(admin_member), "Сделка завершена!",
                                       reply_markup=admin_main_panel())
    elif admin_member:
        await message.answer("Сделка завершена", reply_markup=admin_main_panel())
        await bot_obj.send_message(int(first_member), "Сделка завершена!",
                                   reply_markup=main_panel())

    if second_member and second_member != 'None':
        await bot_obj.send_message(int(second_member), "Сделка завершена!",
                                   reply_markup=main_panel())





#------------------------------------------------------
async def get_data_of_meeting_from_state(state, message_obj, Admin_sector):
    """
    Достает все данные Сделки с Состояния. Если такой Сделки не существует, то переводим юзеров на иг главное меню
    :param state: state (состояние) с телеграм бота
    :param message_obj: обект сообщения с телеграм бота
    :param Admin_sector: класс для состояния для админа
    :return: Возвращает все данные Сделки
    """
    data_meeting = await state.get_data()
    meeting = Meetings().select_one(id_meeting=data_meeting['id_meeting'])

    # Если нету Сделки, то чистим данные юзеров
    if not meeting:
        if message_obj.chat.id in ADMINS:
            await message_obj.answer("<b>Админ-панель</b>", reply_markup=admin_main_panel(), parse_mode='html')
            await Admin_sector.box.set()
            return
        await message_obj.answer('<b>Главное меню</b>', reply_markup=main_panel(), parse_mode='html')
        await state.finish()

    return meeting

async def join_to_meeting_and_send_message(state, message, Meeting_sector):
    checked_message = check_url_meeting(message)
    if checked_message.get('status'):
        meeting = checked_message.get('meeting')
        await message.answer(
            f"Вы успешно присоединились к сделке № {meeting.get('id_meeting')}\n\n Вы общаетесь с пользователем {meeting.get('first_member')}",
            reply_markup=control_panel_for_second_member())
        await Meeting_sector.box.set()
        await state.update_data(id_meeting=meeting.get('id_meeting'), first_member=meeting.get('first_member'),
                                second_member=message.chat.id, admin=meeting.get('admin'),
                                url_meeting=meeting.get('url_meeting'))