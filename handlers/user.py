import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMIN_IDS
from keyboards.user_kb import LANGUAGE_SELECTION, catalog_keyboard, main_keyboard
from states.support import SupportState

# Create router and logger for this handler module
router = Router()
LOG_PATH = Path(__file__).resolve().parent.parent / "logs"
LOG_PATH.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH / "support.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

# In-memory storage of selected language per user.
# This is a simple user session map for language preference.
USER_LANG: dict[int, str] = {}

# Localized bot texts for each supported language.
# Keys are language codes and values are translation maps.
LANGUAGE_STRINGS = {
    "uk": {
        "welcome": (
            'Привіт! Я бот видавництва "Вербель"\n'
            'Оберіть мову, будь ласка.'
        ),
        "language_set": "✅ Мову вибрано! Ось меню.",
        "help": "Наш сайт:\nhttps://www.verbel.org/",
        "catalog_header": "📚 Ось наш каталог:",
        "write_prompt": "✍️ Напишіть повідомлення для адміністратора",
        "send_media_prompt": (
            "📎 Надішліть будь-який файл:\n"
            "фото, відео, pdf, docx, zip або інше."
        ),
        "message_sent": "✅ Повідомлення відправлено адміністраторам!",
        "media_sent": "✅ Ваш файл отримано і надіслано адміністраторам!",
        "admin_message_header": "📩 Нове повідомлення",
        "admin_media_header": "📎 Нове медіа від користувача",
        "reply_admin_prompt": (
            "📝 Тепер напишіть відповідь, і я надішлю її користувачу.\n\n"
            "Введіть /cancel щоб скасувати."
        ),
        "cancelled": (
            "❌ Ви скасували режим відповіді.\n"
            "Можете продовжити роботу."
        ),
        "lang_not_found": "❌ Мову не знайдено. Спробуйте ще раз.",
        "book_not_found": "Книгу не знайдено",
    },
    "en": {
        "welcome": "Hello! I am the Verbel publishing bot.\nPlease choose your language.",
        "language_set": "✅ Language selected! Here is the menu.",
        "help": "Our website:\nhttps://www.verbel.org/",
        "catalog_header": "📚 Here is our catalog:",
        "write_prompt": "✍️ Write a message to the administrator",
        "send_media_prompt": (
            "📎 Send any file:\n"
            "photo, video, pdf, docx, zip or other."
        ),
        "message_sent": "✅ Message sent to the administrators!",
        "media_sent": "✅ Your file was received and sent to the administrators!",
        "admin_message_header": "📩 New message",
        "admin_media_header": "📎 New media from user",
        "reply_admin_prompt": (
            "📝 Now write the answer and I will send it to the user.\n\n"
            "Type /cancel to cancel."
        ),
        "cancelled": "❌ You cancelled reply mode. You can continue working.",
        "lang_not_found": "❌ Language not found. Please try again.",
        "book_not_found": "Book not found",
    },
}

# Catalog book data with localized titles
BOOKS = {
    "book1": {
        "uk": "Гаряче Серце на імʼя Джо Голдер",
        "en": "Hot Heart named Joe Holder",
        "link": "",
    },
    "book2": {
        "uk": 'Журнал "Вербель". Випуск 1',
        "en": "Verbel Magazine issue 1",
        "link": "https://www.verbel.org/product-page/",
    },
}

# Mapping of admin message IDs to user IDs for reply forwarding.
ADMIN_REPLY_MAP: dict[tuple[int, int], int] = {}

# Get the currently selected language for the user or default to Ukrainian.
def get_user_language(user_id: int) -> str:
    return USER_LANG.get(user_id, "uk")

# Set user language only when the selected code is supported.
def set_user_language(user_id: int, language: str) -> None:
    if language in LANGUAGE_STRINGS:
        USER_LANG[user_id] = language

# Get localized text by key using the user's selected language.
def get_text(user_id: int, key: str) -> str:
    language = get_user_language(user_id)
    return LANGUAGE_STRINGS.get(language, LANGUAGE_STRINGS["uk"]).get(key, "")

# Create admin reply inline keyboard for a given user.
# The callback data includes the target user ID to route replies.
def build_reply_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Відповісти користувачу",
                    callback_data=f"reply_user:{user_id}",
                )
            ]
        ]
    )

# Send user support message to all admins
async def notify_admins(message: Message, header: str) -> None:
    content_type = message.content_type
    logger.info(
        "Support request from %s (%s) type=%s",
        message.from_user.full_name,
        message.from_user.id,
        content_type,
    )

    for admin_id in ADMIN_IDS:
        await message.bot.send_message(
            admin_id,
            (
                f"{header}\n\n"
                f"👤 {message.from_user.full_name}\n"
                f"🆔 {message.from_user.id}"
            ),
            reply_markup=build_reply_keyboard(message.from_user.id),
        )
        copied = await message.copy_to(admin_id)
        ADMIN_REPLY_MAP[(admin_id, copied.message_id)] = message.from_user.id

# Handle /start and show the language selection keyboard
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        get_text(message.from_user.id, "welcome"),
        reply_markup=LANGUAGE_SELECTION,
    )

# Handle user's language choice from callback buttons
@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery) -> None:
    language = callback.data.split(":", 1)[1]
    set_user_language(callback.from_user.id, language)
    await callback.answer()
    await callback.message.answer(
        get_text(callback.from_user.id, "language_set"),
        reply_markup=main_keyboard(language),
    )

# Help command replies in the user's language
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(get_text(message.from_user.id, "help"))

# Catalog button opens localized catalog keyboard
@router.message(F.text.in_({"📚 Каталог", "📚 Catalog"}))
async def cmd_catalog(message: Message) -> None:
    await message.answer(
        get_text(message.from_user.id, "catalog_header"),
        reply_markup=catalog_keyboard(get_user_language(message.from_user.id)),
    )

# Write button starts support message flow
@router.message(F.text.in_({"✍️ Написати", "✍️ Write"}))
async def write_admin(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportState.waiting_message)
    await message.answer(get_text(message.from_user.id, "write_prompt"))

# Send media button starts support media flow
@router.message(F.text.in_({"🎥 Відправити медіа", "🎥 Send media"}))
async def send_media(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportState.waiting_media)
    await message.answer(get_text(message.from_user.id, "send_media_prompt"))

# Book callback replies with localized title and link
@router.callback_query(F.data.startswith("book"))
async def check_book(callback: CallbackQuery) -> None:
    book = BOOKS.get(callback.data)
    if not book:
        await callback.answer(get_text(callback.from_user.id, "book_not_found"))
        return

    title = book.get(get_user_language(callback.from_user.id), book["uk"])
    link = book["link"]
    await callback.message.answer(f'📖 "{title}"\n\n{link}')
    await callback.answer()

# Handle text support message from the user
@router.message(SupportState.waiting_message)
async def admin_message(message: Message, state: FSMContext) -> None:
    await notify_admins(message, header=get_text(message.from_user.id, "admin_message_header"))
    await message.answer(get_text(message.from_user.id, "message_sent"))
    await state.clear()

# Handle media support message from the user
@router.message(SupportState.waiting_media)
async def admin_media(message: Message, state: FSMContext) -> None:
    await notify_admins(message, header=get_text(message.from_user.id, "admin_media_header"))
    await message.answer(get_text(message.from_user.id, "media_sent"))
    await state.clear()

# Admin starts reply mode with button callback
@router.callback_query(F.data.startswith("reply_user:"))
async def start_admin_reply(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = int(callback.data.split(":", 1)[1])
    await state.set_state(SupportState.waiting_admin_response)
    await state.update_data(reply_target_id=user_id)
    await callback.answer("Напишіть відповідь користувачу у цьому чаті.")
    await callback.message.answer(
        "📝 Тепер напишіть відповідь, і я надішлю її користувачу.\n\n"
        "Введіть /cancel щоб скасувати.",
        reply_markup=None,
    )

# Cancel admin reply mode
@router.message(SupportState.waiting_admin_response, Command("cancel"))
async def cancel_admin_reply(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Ви скасували режим відповіді.\n"
        "Можете продовжити роботу.",
        reply_markup=None,
    )

# Send admin reply to the target user
@router.message(SupportState.waiting_admin_response)
async def send_admin_reply(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    target_user_id = data.get("reply_target_id")
    if target_user_id is None:
        await message.answer(
            "❌ Не вдалося знайти користувача для цієї відповіді. Спробуйте ще раз."
        )
        await state.clear()
        return

    try:
        await message.copy_to(target_user_id)
        logger.info(
            "Admin %s replied to user %s, type=%s",
            message.from_user.id,
            target_user_id,
            message.content_type,
        )
        await message.answer("✅ Відповідь надіслано користувачу.")
    except Exception as e:
        logger.error(
            "Failed to send reply to user %s: %s",
            target_user_id,
            str(e),
        )
        await message.answer(f"❌ Помилка при надсиланні відповіді: {str(e)}")
    finally:
        await state.clear()

# Admin reply by direct reply-to-user message
@router.message(lambda message: message.from_user.id in ADMIN_IDS and message.reply_to_message is not None)
async def reply_to_user(message: Message) -> None:
    reply = message.reply_to_message
    target_user_id = ADMIN_REPLY_MAP.get((message.from_user.id, reply.message_id))
    if target_user_id is None and reply.forward_from is not None:
        target_user_id = reply.forward_from.id
    if target_user_id is None:
        await message.answer("❌ Не вдалося знайти користувача для цієї відповіді.")
        return

    try:
        await message.copy_to(target_user_id)
        logger.info(
            "Admin %s replied by reply-to-message to user %s, type=%s",
            message.from_user.id,
            target_user_id,
            message.content_type,
        )
        await message.answer("✅ Відповідь надіслано користувачу.")
    except Exception as e:
        logger.error(
            "Failed to send reply-to-message to user %s: %s",
            target_user_id,
            str(e),
        )
        await message.answer(f"❌ Помилка при надсиланні: {str(e)}")
