from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ==========================
# MAIN KEYBOARD
# ==========================
main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📚 Каталог"
            )
        ],
        [
            KeyboardButton(
                text="✍️ Написати"
            )
        ],
        [
            KeyboardButton(
                text="🎥 Відправити медіа"
            )
        ]
    ],
    resize_keyboard=True
)


# ==========================
# CATALOG KEYBOARD
# ==========================
catalog = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Гаряче Серце на імʼя Джо Голдер",
                callback_data="book1"
            )
        ],
        [
            InlineKeyboardButton(
                text='Журнал "Вербель"',
                callback_data="book2"
            )
        ]
    ]
)