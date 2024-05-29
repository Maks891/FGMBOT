from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import TELEGRAM_CHANNEL
import random


def back_key():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Назад')
	key.insert(b1)
	return key

def go_to_URL_key(URL):
	key = InlineKeyboardMarkup()
	b1 = InlineKeyboardButton(text='Перейти', url=URL)
	key.row(b1)
	return key

def main_panel():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Начать сделку')
	key.insert(b1)
	b1 = KeyboardButton('Правила сервиса')
	key.insert(b1)
	b1 = KeyboardButton('Способы оплаты')
	key.insert(b1)
	b1 = KeyboardButton('Рейтинг и отзывы')
	key.insert(b1)
	return key

def control_panel():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Удалить собеседника')
	key.insert(b1)
	b1 = KeyboardButton('Вызвать Гаранта')
	key.insert(b1)
	b1 = KeyboardButton('Завершить Сделку')
	key.insert(b1)
	return key

def control_panel_for_second_member():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Вызвать Гаранта')
	key.insert(b1)
	b1 = KeyboardButton('Выйти со сделки')
	key.insert(b1)
	return key

#______________________________________________________________________#
def admin_main_panel():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Вызовы гаранта')
	key.insert(b1)
	b1 = KeyboardButton('Текущие Сделки')
	key.insert(b1)
	b1 = KeyboardButton('Статистика')
	key.insert(b1)
	b1 = KeyboardButton('Рассылка')
	key.insert(b1)
	return key


def join_to_meeting(id_meeting):
	key = InlineKeyboardMarkup()
	b1 = InlineKeyboardButton(text='Присоединится', callback_data=f'join:{id_meeting}')
	key.row(b1)
	b1 = InlineKeyboardButton(text='Удалить сделку', callback_data=f'remove:{id_meeting}')
	key.row(b1)
	return key

def control_panel_for_admin_member():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Посмотреть все сообщения')
	key.insert(b1)
	b1 = KeyboardButton('Завершить Сделку')
	key.insert(b1)
	b1 = KeyboardButton('Выйти со сделки')
	key.insert(b1)
	return key