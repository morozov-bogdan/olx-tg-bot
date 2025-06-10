import asyncio
import logging
import sys
import keyboard
import fetch_olx_ads as foa


from bs4 import BeautifulSoup
from config import TOKEN
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Приветствую {message.from_user.first_name}", reply_markup=keyboard.kb_start)


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
    
    await message.answer(f"🔍 Ищу объявления по запросу: {query}...")

    try:
        ads = foa.get_olx_ads(query)

        for i in range(len(ads['title'])):
            await message.answer(f'{i+1}. <b>{ads['title'][i]}</b>\n💵 {ads['price'][i]}\n📍 {ads['location_date'][i]}\n🔗 https://www.olx.ua{ads['link'][i]}', 
                                 parse_mode='HTML',
                                 disable_web_page_preview=True,
                                 disable_notification=True
            )
            if i+1 == 20:
                break

    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


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