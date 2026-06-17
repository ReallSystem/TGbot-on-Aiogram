from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Keyboard for initial language selection
LANGUAGE_SELECTION = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Українська", callback_data="lang:uk"),
            InlineKeyboardButton(text="English", callback_data="lang:en"),
        ]
    ]
)

# Main keyboard layouts for Ukrainian and English users
MAIN_KEYBOARDS = {
    "uk": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог")],
            [KeyboardButton(text="✍️ Написати")],
            [KeyboardButton(text="🎥 Відправити медіа")],
        ],
        resize_keyboard=True,
    ),
    "en": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Catalog")],
            [KeyboardButton(text="✍️ Write")],
            [KeyboardButton(text="🎥 Send media")],
        ],
        resize_keyboard=True,
    ),
}

# Localized book titles for the catalog buttons.
CATALOG_TITLES = {
    "uk": [
        "Гаряче Серце на імʼя Джо Голдер",
        'Журнал "Вербель"',
    ],
    "en": [
        "Hot Heart named Joe Holder",
        "Verbel Magazine issue 1",
    ],
}

# Return the main keyboard for the current user language.
def main_keyboard(language: str = "uk") -> ReplyKeyboardMarkup:
    return MAIN_KEYBOARDS.get(language, MAIN_KEYBOARDS["uk"])

# Return the catalog keyboard with titles in the current language.
def catalog_keyboard(language: str = "uk") -> InlineKeyboardMarkup:
    titles = CATALOG_TITLES.get(language, CATALOG_TITLES["uk"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=titles[0], callback_data="book1")],
            [InlineKeyboardButton(text=titles[1], callback_data="book2")],
        ]
    )
