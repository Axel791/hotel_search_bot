from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

buttons = ['Главное меню']
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(*buttons)


inline_kb1 = InlineKeyboardButton('Самая высокая цена💰⏫', callback_data='button1')
inline_kb2 = InlineKeyboardButton('Самая низкая цена💰⏬', callback_data='button2')
inline_kb3 = InlineKeyboardButton('Лучшее предложение🔝', callback_data='button3')
inline_kb4 = InlineKeyboardButton('Просмотреть историю📝', callback_data='button_4')
inline_kb5 = InlineKeyboardButton('Да', callback_data='yes')
inline_kb6 = InlineKeyboardButton('Нет', callback_data='no')
inline_kb7 = InlineKeyboardButton('<<Назад', callback_data='Back')
inline_kb8 = InlineKeyboardButton('Отмена', callback_data='cancel')
inline_kb9 = InlineKeyboardButton('Найти отели🔍', callback_data='find_hotels')
inline_kb10 = InlineKeyboardButton('<<Назад', callback_data='Back_2')
inline_kb11 = InlineKeyboardButton('<<Назад', callback_data='Back_3')

inline_buttons_1 = InlineKeyboardMarkup().add(inline_kb1).add(inline_kb2).add(inline_kb3).add(inline_kb10)
inline_buttons_2 = InlineKeyboardMarkup().add(inline_kb5, inline_kb6).add(inline_kb8)
inline_buttons_3 = InlineKeyboardMarkup().add(inline_kb7)
inline_buttons_4 = InlineKeyboardMarkup().add(inline_kb8)
inline_buttons_5 = InlineKeyboardMarkup().add(inline_kb9).add(inline_kb4)
inline_buttons_6 = InlineKeyboardMarkup().add(inline_kb11)
