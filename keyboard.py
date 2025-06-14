from aiogram import types
from aiogram.types import InlineKeyboardButton


keyboard_start = [
    [types.KeyboardButton(text='Информация про товар')],
    [types.KeyboardButton(text='Проверка продавца')],
    [types.KeyboardButton(text='Поиск товара')],
    [types.KeyboardButton(text='Мой профиль')],
    [types.KeyboardButton(text='Тех.подержка')]
]

start = types.ReplyKeyboardMarkup(keyboard=keyboard_start, resize_keyboard=True)