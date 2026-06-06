from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Написати'),
         KeyboardButton(text='Відправити медіа')]
    ],
    resize_keyboard=True,
    input_placeholder='Виберіть пункт меню'
)

catalog = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='"Гаряче Серце на ім\'я Джо Голдер"', callback_data='book_Holder')],
        [InlineKeyboardButton(text='Журнал "Вербель". Випуск 1', callback_data='book_book2')],
        [InlineKeyboardButton(text='Категорія 3', callback_data='book_book3')]
    ]
)