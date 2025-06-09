from aiogram import types


keyboard_start = [
    [types.KeyboardButton(text='Информация про товар')],
    [types.KeyboardButton(text='Проверка продавца')],
    [types.KeyboardButton(text='Поиск товара')],
    [types.KeyboardButton(text='Мой профиль')],
    [types.KeyboardButton(text='Тех.подержка')]
]

kb_start = types.ReplyKeyboardMarkup(keyboard=keyboard_start, resize_keyboard=True)