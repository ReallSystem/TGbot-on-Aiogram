from aiogram import Bot, Dispatcher, F, Router
import keyboards as kb
from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart

user = Router()







@user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привіт! Моє імення Вербелик. Скористайтесь меню знизу',
                         reply_markup=ReplyKeyboardRemove())
                        


@user.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Посилання на сайт: verbelly.net\n\n')

@user.message(F.photo)
async def cmd_photo(message: Message):
    await message.answer( f'Дякую за фото!\n\n')
    await message.answer_photo(photo=message.photo[-2].file_id)


@user.message(F.document)
async def cmd_document(message: Message):
    await message.answer(f'Дякую за файл!\n\n')
    await message.answer_document(document=message.document.file_id)

@user.message(F.text == 'Каталог')
async def cmd_catalog(message: Message):
    await message.answer('Ось наш каталог:', 
                         reply_markup=kb.catalog)
    

@user.callback_query(F.data.startswith('book_'))
async def check_book(callback: CallbackQuery):
    brand_name = callback.data.split('_')[1]
    await callback.answer(f'Ось посилання на книгу "Гаряче Серце на ім\'я Джо Голдер":\n\nhttps://verbelly.net/knigi/garache-serce-na-imya-dzho-golder/')
    await callback.message.answer(f'Ось посилання на книгу "Гаряче Серце на ім\'я Джо Голдер":\n\nhttps://verbelly.net/knigi/garache-serce-na-imya-dzho-golder/')

@user.callback_query(F.data == 'book2')
async def check_book(callback: CallbackQuery):
    await callback.message.answer('Ось посилання на книгу "Журнал "Вербель". Випуск 1":\n\nhttps://verbelly.net/knigi/verbel-zhurnal-vipusk-1/')
    await callback.answer('Ось посилання на книгу "Журнал "Вербель". Випуск 1":\n\nhttps://verbelly.net/knigi/verbel-zhurnal-vipusk-1/')

@user.callback_query(F.data == 'book3')
async def check_book(callback: CallbackQuery):
    await callback.message.answer('Ось посилання на книгу "Категорія 3":\n\nhttps://verbelly.net/knigi/kategorija-3/')




