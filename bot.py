import asyncio
import logging
import sys
import keyboard
import fetch_olx_ads as fetch_oa
import arenda_olx_ads as arenda_oa


from config import TOKEN

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, html, types, F, exceptions
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder


dp = Dispatcher()
last_search_time_article = {}
last_search_time_arenda = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Приветствую {message.from_user.first_name}")
    

@dp.message(Command('search'))
async def search_article(message: Message):
    query = message.text.replace('/search', '').strip()
    if not query:
        await message.answer("Пожалуйста, укажите поисковый запрос после команды /search")
        return

    current_datetime = datetime.now()
    if message.from_user.id in last_search_time_article: # добавление кд для поиска вещи в 30 секунд
            last_time = last_search_time_article[message.from_user.id]
            if current_datetime - last_time < timedelta(seconds=30):
                await message.answer("Пожалуйста подождите 30 секунд перед новым запросом.")
                return


    await message.answer(f"🔍 Ищу объявления по запросу: {query}... \n⏳ Среднее время поиска ~20 секунд")
    ads = fetch_oa.get_olx_ads(query, offset=0, limit=20)

    for i in range(len(ads['title'])):
        await message.answer(f'{i+1}. <b>{ads['title'][i]}</b>\n💵 {ads['price'][i]}\n📍 {ads['location_date'][i]}\n🔗 https://www.olx.ua{ads['link'][i]}', 
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                disable_notification=True
        )
        if i+1 >= 20:
            kb_show_more_article = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Да",
                        callback_data=f"show_more_article:{query}:20"  # query и offset=20
                    )]
                ]
            )
            await message.answer("Загрузить ещё?", reply_markup=kb_show_more_article)
    
    last_search_time_article[message.from_user.id] = current_datetime
    
@dp.callback_query(F.data.startswith("show_more_article:"))
async def show_more_article(call: CallbackQuery):
    _, query, offset = call.data.split(':')
    offset = int(offset)

    ads = fetch_oa.get_olx_ads(query, offset=offset, limit=20)

    if not ads['title']:
        await(f'К сожалению, не смог найти больше объявлений')
        return
    
    await call.message.answer(f"🔍 Продолжаю поиск объявлений по запросу: {query}... \n⏳ Среднее время поиска ~20 секунд")
    for i in range(len(ads['title'])):
        await call.message.answer(f'{i+1}. <b>{ads['title'][i]}</b>\n💵 {ads['price'][i]}\n📍 {ads['location_date'][i]}\n🔗 https://www.olx.ua{ads['link'][i]}', 
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                disable_notification=True
        )


    new_offset = offset + 20
    kb_show_more_article = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Да",
                callback_data=f"show_more_article:{query}:{new_offset}"
            )]
        ]
    ) 

    await call.message.answer("Загрузить ещё?", reply_markup=kb_show_more_article)
    try:
        await call.answer()
    except exceptions.TelegramBadRequest as e:
        if 'query is too old' in e:
            pass
        else:
            raise e

@dp.message(Command('arenda'))
async def search_arenda(message: Message):
    args = message.text.split(maxsplit=3)[1:]

    if len(args) <= 0: 
        await message.reply('<b>❔ Пожалуйста введите команду: <i>/arenda "город" "валюта"* "cортировка"*</i>\n❗ Обозначение "*", являеться необязательным параметром при запросе</b>', parse_mode='HTML')
        return

    arg1 = args[0]
    arg2 = args[1] if len(args) >= 2 else None
    arg3 = args[2] if len(args) >= 3 else None

    
    valid_city = False
    for c in arenda_oa.city_list:
        if arg1 == c:
            valid_city = True
            break
    if valid_city == False:
        await message.reply('К сожалению мы можем работать только с областными городами, например: киев, одесса, харьков и т.д.')
        return
            
    check_sort_keys = ['1', '2', '3']
    check_valid_currency = ['USD', 'UAH', 'ЮСД', 'ЮАН'] 

    if arg2 != None and arg2.upper() not in check_valid_currency:
        await message.reply("Доступны такие виды валют:\n'USD', 'UAH'")
        return
    if arg3 != None and arg3.lower() not in check_sort_keys:
        await message.reply("При выборе сортировке впишите цифру варианта:\n1. От дешёвых к дорогим\n2. От дорогих к дешёвым\n3. Рекомендованные")
        return

    current_datetime = datetime.now()
    if message.from_user.id in last_search_time_arenda:


        last_time = last_search_time_arenda[message.from_user.id]
        if current_datetime - last_time < timedelta(seconds=60):
            await message.answer("Пожалуйста подождите 60 секунд перед новым запросом.")
            return

    await message.answer('🔍 Начал поиск аренды...\n⏳ Среднее время ответа на запрос ~20 секунд')
    
    ads = arenda_oa.get_olx_arenda(city=arg1, currency=arg2, sort=arg3, offset=0, limit=20)

    for i in range((len(ads['title']))):
        await message.answer(f'<b>{ads['title'][i]}</b>\n💵 <b>{ads['price'][i]}</b>\n📍 {ads['location_date'][i]}\n<a href="https://www.olx.ua{ads['link'][i]}">Ссылка</a>',
                             parse_mode='HTML',
                             disable_notification=True)
        if i+1 >= 20:
            callback = f'show_more_arenda:{arg1}:20'
            if arg2 != None: callback = callback+f':{arg2}'
            if arg3 != None: callback = callback+f':{arg3}'

            kb_show_more_article = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Да",
                        callback_data=callback
                    )]
                ]
            )
            await message.answer("Загрузить ещё?", reply_markup=kb_show_more_article)
           

    last_search_time_arenda[message.from_user.id] = current_datetime


@dp.callback_query(F.data.startswith("show_more_arenda:"))
async def show_more_arenda(call: CallbackQuery):
    callback_query = call.data.split(':')
    
    city = callback_query[1]
    offset = int(callback_query[2])
    
    currency = callback_query[3] if len(callback_query) > 3 else None
    sort = callback_query[4] if len(callback_query) > 4 else None

    ads = arenda_oa.get_olx_arenda(city=city, offset=offset, currency=currency, sort=sort, limit=20)
    if not ads['title']:
        await call.message.answer('К сожалению более не нашёл объявлений')
        return
    

    for i in range((len(ads['title']))):
        await call.message.answer(f'<b>{ads['title'][i]}</b>\n💵 <b>{ads['price'][i]}</b>\n📍 {ads['location_date'][i]}\n<a href="https://www.olx.ua{ads['link'][i]}">Ссылка</a>',
                             parse_mode='HTML',
                             disable_notification=True)
        
    new_offset = offset + 20
    callback = f'show_more_arenda:{city}:{new_offset}'
    if currency != None: callback = callback+f':{currency}'
    if sort != None: callback = callback+f':{sort}'

    kb_show_more_arenda = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Да",
                callback_data=callback
            )]
        ]
    )

    await call.message.answer("Загрузить ещё?", reply_markup=kb_show_more_arenda)
    try:
        await call.answer()
    except exceptions.TelegramBadRequest as e:
        if 'query is too old' in e:
            pass
        else:
            raise e




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())