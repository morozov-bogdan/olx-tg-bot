import asyncio
import logging
import sys
import keyboard
import fetch_olx_ads as foa
import arenda_olx_ads as arenda_oa


from bs4 import BeautifulSoup
from config import TOKEN
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from datetime import datetime, timedelta


dp = Dispatcher()
last_search_time_article = {}
last_search_time_arenda = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Приветствую {message.from_user.first_name}")
    # await message.answer(f"Приветствую {message.from_user.first_name}", reply_markup=keyboard.kb_start)


@dp.message(Command('stop'))
async def stop_bot(message: Message):
    await message.answer('Бот был остановлен', reply_markup=ReplyKeyboardRemove())


@dp.message(F.text.lower() == 'информация про товар')
async def info_for_article(message: Message):
    pass


@dp.message(F.text.lower() == 'проверка продавца')
async def check_seller(message: Message):
    pass


# @dp.message(F.text.lower() == 'поиск товара')
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

    await message.answer(f"🔍 Ищу объявления по запросу: {query}...")
    ads = foa.get_olx_ads(query)


    for i in range(len(ads['title'])):
        await message.answer(f'{i+1}. <b>{ads['title'][i]}</b>\n💵 {ads['price'][i]}\n📍 {ads['location_date'][i]}\n🔗 https://www.olx.ua{ads['link'][i]}', 
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                disable_notification=True
        )
        if i+1 >= 20:
            break
    
    last_search_time_article[message.from_user.id] = current_datetime
    


@dp.message(Command('arenda'))
async def search_arenda(message: Message):
    args = message.text.split(maxsplit=3)[1:]

    if len(args) <= 0: 
        await message.reply('<b>Пожалуйста введите команду: <i>/arenda "город" "валюта"* "cортировка"*</i>\nОбозначение "*", являеться необязательным параметром при запросе</b>', parse_mode='HTML')
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

    if arg2 != None and arg2.lower() not in check_sort_keys:
        await message.reply("При выборе сортировке впишите цифру варианта:\n1. От дешёвых к дорогим\n2. От дорогих к дешёвым\n3. Рекомендованные")
        return
    if arg3 != None and arg3.upper() not in check_valid_currency:
        await message.reply("Доступны такие виды валют:\n'USD', 'UAH'")
        return


    current_datetime = datetime.now()
    if message.from_user.id in last_search_time_arenda:


        last_time = last_search_time_arenda[message.from_user.id]
        if current_datetime - last_time < timedelta(seconds=60):
            await message.answer("Пожалуйста подождите 60 секунд перед новым запросом.")
            return


    ads = arenda_oa.get_olx_arenda(city=arg1, sort=arg2, currency=arg3)

    for i in range((len(ads['title']))):
        await message.answer(f'<b>{ads['title'][i]}</b>\n💵 <b>{ads['price'][i]}</b>\n📍 {ads['location_date'][i]}\n<a href="https://www.olx.ua{ads['link'][i]}">Ссылка</a>',
                             parse_mode='HTML',
                             disable_notification=True)
        if i+1 >= 20:
            break
    
    last_search_time_arenda[message.from_user.id] = current_datetime


@dp.message(F.text.lower() == 'мой профиль')
async def my_profile(message: Message):
    pass


@dp.message(F.text.lower() == 'тех.подержка')
async def create_tiket(message: Message):
    pass


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())