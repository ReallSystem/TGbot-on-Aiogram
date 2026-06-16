import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMIN_IDS
from keyboards.user_kb import catalog, main
from states.support import SupportState

router = Router()


LOG_PATH = Path(__file__).resolve().parent.parent / "logs"
LOG_PATH.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH / "support.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


BOOKS = {
    "book1": (
        "Гаряче Серце на імʼя Джо Голдер",
        ""
    ),
    "book2": (
        'Журнал "Вербель". Випуск 1',
        "https://www.verbel.org/product-page/"
    )
}

ADMIN_REPLY_MAP: dict[tuple[int, int], int] = {}


def build_reply_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Відповісти користувачу",
                    callback_data=f"reply_user:{user_id}"
                )
            ]
        ]
    )


async def notify_admins(message: Message, header: str) -> None:
    """Надіслати адміністратору переслане повідомлення користувача."""
    content_type = message.content_type
    logger.info(
        "Support request from %s (%s) type=%s",
        message.from_user.full_name,
        message.from_user.id,
        content_type,
    )

    for admin_id in ADMIN_IDS:
        info_message = await message.bot.send_message(
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


# ==========================
# START
# ==========================
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        'Привіт! Я бот видавництва "Вербель"\n'
        'Скористайтесь меню знизу.\n'
        'P.S. Ми відкриті до співпраці.',
        reply_markup=main,
    )
# ==========================
# HELP
# ==========================
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Наш сайт:\n"
        "https://www.verbel.org/"
    )
# ==========================
# КАТАЛОГ
# ==========================
@router.message(F.text == "📚 Каталог")
async def cmd_catalog(message: Message) -> None:
    await message.answer(
        "📚 Ось наш каталог:",
        reply_markup=catalog,
    )


# ==========================
# НАПИСАТИ
# ==========================
@router.message(F.text == "✍️ Написати")
async def write_admin(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportState.waiting_message)
    await message.answer(
        "✍️ Напишіть повідомлення для адміністратора"
    )


# ==========================
# ВІДПРАВИТИ МЕДІА
# ==========================
@router.message(F.text == "🎥 Відправити медіа")
async def send_media(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportState.waiting_media)
    await message.answer(
        "📎 Надішліть будь-який файл:\n"
        "фото, відео, pdf, docx, zip або інше."
    )


# ==========================
# BOOK CALLBACK
# ==========================
@router.callback_query(F.data.startswith("book"))
async def check_book(callback: CallbackQuery) -> None:
    book = BOOKS.get(callback.data)
    if not book:
        await callback.answer("Книгу не знайдено")
        return

    title, link = book
    await callback.message.answer(f'📖 "{title}"\n\n{link}')
    await callback.answer()


# ==========================
# SUPPORT MESSAGE
# ==========================
@router.message(SupportState.waiting_message)
async def admin_message(message: Message, state: FSMContext) -> None:
    await notify_admins(message, header="📩 Нове повідомлення")
    await message.answer("✅ Повідомлення відправлено адміністраторам!")
    await state.clear()


# ==========================
# SUPPORT MEDIA
# ==========================
@router.message(SupportState.waiting_media)
async def admin_media(message: Message, state: FSMContext) -> None:
    await notify_admins(message, header="📎 Нове медіа від користувача")
    await message.answer("✅ Ваш файл отримано і надіслано адміністраторам!")
    await state.clear()


# ==========================
# ADMIN REPLY BUTTON
# ==========================
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


# ==========================
# CANCEL ADMIN REPLY
# ==========================
@router.message(SupportState.waiting_admin_response, Command("cancel"))
async def cancel_admin_reply(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Ви скасували режим відповіді.\n"
        "Можете продовжити роботу.",
        reply_markup=None,
    )


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
        await message.answer(
            f"❌ Помилка при надсиланні відповіді: {str(e)}"
        )
    finally:
        await state.clear()


@router.message(lambda message: message.from_user.id in ADMIN_IDS and message.reply_to_message is not None)
async def reply_to_user(message: Message) -> None:
    reply = message.reply_to_message
    target_user_id = ADMIN_REPLY_MAP.get((message.from_user.id, reply.message_id))

    if target_user_id is None and reply.forward_from is not None:
        target_user_id = reply.forward_from.id

    if target_user_id is None:
        await message.answer(
            "❌ Не вдалося знайти користувача для цієї відповіді."
        )
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
        await message.answer(
            f"❌ Помилка при надсиланні: {str(e)}"
        )