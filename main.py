import logging

import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.callback_query import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import *
from key import *
from services import create_new_meetings, is_member_in_meeting, remove_second_member, write_down_message, is_user_in_db, \
	send_list_of_meetings, remove_meeting, join_to_meeting_admin, send_all_messages_of_meeting, \
	end_meeting, get_data_of_meeting_from_state, join_to_meeting_and_send_message, send_meetings_that_need_garant, \
	send_error_to_join_admin_as_member, get_statistics_bot, make_mailing_to_all, logout_from_meeting, \
	call_garanta_for_meeting
from texts_bot import ways_to_pay, rules_bot

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_BOT)
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

class Admin_sector(StatesGroup):
	box = State()

class Meeting_sector(StatesGroup):
	id_meeting = State()
	first_member = State()
	second_member = State()
	admin = State()
	url_meeting = State()

	box = State() # Тут будет весь разговор

class Mailing_sector(StatesGroup):
	text_mailing = State()

# команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
	is_user_in_db(message.chat.id)

	"""Проверяем перешел ли юзер по ссылке на какую-то сделку"""
	if len(message.text.split(' ')) == 2:

		# Если юзер является админом, то выдаем ошибку, что он не может присоединится
		if not await send_error_to_join_admin_as_member(Admin_sector=Admin_sector, message_obj=message): return

		await join_to_meeting_and_send_message(state=state, message=message, Meeting_sector=Meeting_sector)


	else:
		await message.answer('Приветствую', reply_markup=main_panel())

@dp.message_handler()
async def main(message: types.Message, state: FSMContext):
	is_user_in_db(message.chat.id)

	if message.chat.id in ADMINS and message.text != '/admin':
		await message.answer('Вы админ, напишите /admin')
		return

	# """Проверяем перешел ли юзер по ссылке на какую-то сделку"""
	if '/start' in message:
		if len(message.text.split(' ')) == 2:

			# Если юзер является админом, то выдаем ошибку, что он не может присоединится
			if not await send_error_to_join_admin_as_member(Admin_sector=Admin_sector, message_obj=message): return

			await join_to_meeting_and_send_message(state=state, message=message, Meeting_sector=Meeting_sector)


	elif message.text == "Начать сделку":
		data_meeting = create_new_meetings(message.chat.id)
		if not data_meeting:
			await message.answer("Вы уже есть в <b>другой</b> сделке!", parse_mode='html')
			return

		await message.answer(f"ID сделки <b>{data_meeting.get('id_meeting')}</b>\n\nСсылка для приглашения {data_meeting.get('url_meeting')}", reply_markup=control_panel(), parse_mode='html', disable_web_page_preview=True)

		await Meeting_sector.box.set()
		await state.update_data(id_meeting=data_meeting.get('id_meeting'), first_member=message.chat.id, second_member=None, admin=None, url_meeting=data_meeting.get('url_meeting'))

	elif message.text == 'Рейтинг и отзывы':
		await message.answer("Перейдите в телеграм канал для просмотра рейтинга и отзывов", reply_markup=go_to_URL_key(TELEGRAM_CHANNEL))

	elif message.text == 'Способы оплаты':
		await message.answer(ways_to_pay, reply_markup=go_to_URL_key(MENEDGER))

	elif message.text == 'Правила сервиса':
		await message.answer(rules_bot, reply_markup=main_panel())

	elif message.text == "/admin" and message.chat.id in ADMINS:
		await message.answer("<b>Админ-панель</b>", reply_markup=admin_main_panel(), parse_mode='html')
		await Admin_sector.box.set()


#__________________________________________________________________________________#


@dp.message_handler(state=Meeting_sector.box)
async def meeting_box(message: types.Message, state: FSMContext):
	"""Оболочка для СДЕЛКИ"""
	data_meeting = await get_data_of_meeting_from_state(state, message, Admin_sector)

	# Если сделка не существует
	if not data_meeting:
		return

	if not is_member_in_meeting(id_meeting=data_meeting['id_meeting'], member_id=message.chat.id):
		await message.answer("Вас <b>нет</b> в активной сделке", reply_markup=main_panel(), parse_mode='html')
		await state.finish()
		return

	elif "Удалить собеседника" == message.text and data_meeting.get('first_member') == message.chat.id:
		await remove_second_member(bot, message, data_meeting['id_meeting'])

	elif "Завершить Сделку" == message.text and data_meeting.get('first_member') == message.chat.id:
		await end_meeting(bot, message, data_meeting)
		await state.finish()

	elif 'Выйти со сделки' == message.text:
		await logout_from_meeting(bot=bot, state_obj=state, message_obj=message, Admin_sector=Admin_sector, id_meeting=data_meeting['id_meeting'])

	elif 'Вызвать Гаранта' in message.text:
		await call_garanta_for_meeting(bot=bot, message_obj=message, id_meeting=data_meeting['id_meeting'])

	#_______________________  Админ  ___________________________#

	elif 'Посмотреть все сообщения' == message.text and message.chat.id in ADMINS:
		await send_all_messages_of_meeting(id_meeting=data_meeting['id_meeting'], message=message)

	elif 'Завершить Сделку' == message.text and message.chat.id in ADMINS:
		await end_meeting(bot, message, data_meeting)

	#__________________________________________________________________#

	# Идет записсывание сообщений
	else:

		admin_member, first_member, second_member = data_meeting['admin'], data_meeting['first_member'], data_meeting[
			'second_member']
		users_id = [admin_member, first_member, second_member]
		for user_id in users_id:
			if user_id == message.chat.id:
				continue

			# Ловим ошибку если chat_id пустой или неверный
			if message.chat.id in ADMINS:
				try:
					await bot.send_message(user_id, f"🔱 - ГАРАНТ - 🔱\n\n{message.text}")
				except aiogram.utils.exceptions.ChatIdIsEmpty:
					pass
			else:
				try:
					await bot.send_message(user_id, f"🌀 - {message.from_user.first_name} - 🌀\n\n{message.text}")
				except aiogram.utils.exceptions.ChatIdIsEmpty:
					pass

		if message.chat.id in ADMINS:
			msg = f"🔱 - ГАРАНТ - 🔱\n\n {message.text}"
		else:
			msg = f"☮ [{message.from_user.first_name}] \n\n{message.text}"
		write_down_message(data_meeting['id_meeting'], msg, message.chat.id)


#__________________________________________________________________________________#
@dp.message_handler(state=Admin_sector.box)
async def Admin_sector_msg(message: types.Message, state: FSMContext):
	"""Оболочка для Админ-Панели"""

	if message.text == 'Вызовы гаранта':
		await send_meetings_that_need_garant(message_obj=message)

	elif message.text == 'Текущие Сделки':
		await send_list_of_meetings(message=message)

	elif message.text == 'Статистика':
		statistics = get_statistics_bot()
		await message.answer(statistics, reply_markup=admin_main_panel(), parse_mode='html')

	elif message.text == 'Рассылка':
		await message.answer('Напишите сообщения для рассылки', reply_markup=back_key())
		await Mailing_sector.text_mailing.set()

	elif message.text == "/admin" and message.chat.id in ADMINS:
		await message.answer("<b>Админ панель</b>", reply_markup=admin_main_panel(), parse_mode='html')

@dp.callback_query_handler(state=Admin_sector.box)
async def Admin_sector_call(call: CallbackQuery, state: FSMContext):

	if 'remove' in call.data:
		await remove_meeting(bot_obj=bot, data_call=call)

	elif 'join' in call.data:
		await join_to_meeting_admin(state_obj=state, Meeting_sector=Meeting_sector, data_call=call)

@dp.message_handler(state=Mailing_sector.text_mailing)
async def Mailing_sector_msg(message: types.Message, state: FSMContext):
	if message.text == 'Назад':
		await message.answer("<b>Админ-панель</b>", reply_markup=admin_main_panel(), parse_mode='html')
		await state.finish()
		await Admin_sector.box.set()
		return

	await make_mailing_to_all(bot=bot, message_obj=message)

	await state.finish()
	await Admin_sector.box.set()


if __name__ == '__main__':
	executor.start_polling(dp)