import logging
from pathlib import Path

from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from config import ADMIN_IDS
from handlers.user import (
    ban_user,
    get_all_registered_users,
    get_unbanned_registered_users,
    unban_user,
)


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in ADMIN_IDS)

# Create router and logger for this handler module
router = Router()
LOG_PATH = Path(__file__).resolve().parent.parent / "logs"
LOG_PATH.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH / "admin.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


@router.message(Command(commands=["ban"]), AdminFilter())
async def cmd_ban(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Використання: /ban <user_id>")
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.answer("Невірний user_id. Використання: /ban <user_id>")
        return

    if ban_user(target_user_id):
        await message.answer(f"Користувача {target_user_id} заблоковано.")
        logger.info("Admin %s banned user %s", message.from_user.id, target_user_id)
    else:
        await message.answer(f"Користувач {target_user_id} вже заблокований.")


@router.message(Command(commands=["unban"]), AdminFilter())
async def cmd_unban(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Використання: /unban <user_id>")
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await message.answer("Невірний user_id. Використання: /unban <user_id>")
        return

    if unban_user(target_user_id):
        await message.answer(f"Користувача {target_user_id} розблоковано.")
        logger.info("Admin %s unbanned user %s", message.from_user.id, target_user_id)
    else:
        await message.answer(f"Користувач {target_user_id} не був заблокований.")


@router.message(Command(commands=["broadcast"]), AdminFilter())
async def cmd_broadcast(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Використання: /broadcast <повідомлення>")
        return

    text = parts[1].strip()
    users = get_unbanned_registered_users()
    if not users:
        await message.answer("Немає користувачів для розсилки.")
        return

    sent = 0
    failed = 0
    for user_id in users:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
        except Exception as exc:
            failed += 1
            logger.warning("Broadcast failed for %s: %s", user_id, exc)

    await message.answer(
        f"Розсилка завершена. Відправлено: {sent}, помилок: {failed}."
    )
    logger.info(
        "Admin %s broadcast sent to %s users, failed %s",
        message.from_user.id,
        sent,
        failed,
    )


@router.message(lambda message: message.text is not None and message.text.split(maxsplit=1)[0].lower().startswith("/users"))
async def cmd_users(message: Message) -> None:
    if not message.from_user or message.from_user.id not in ADMIN_IDS:
        await message.answer("Тільки для адміністраторів.")
        return

    users = get_all_registered_users()
    count = len(users)
    if count == 0:
        await message.answer("Немає зареєстрованих користувачів.")
        return

    user_list_text = "\n".join(str(user_id) for user_id in users[:50])
    more_text = "\n..." if count > 50 else ""
    await message.answer(
        f"Зареєстровані користувачі ({count}):\n{user_list_text}{more_text}"
    )


@router.message(lambda message: message.text is not None and message.text.split(maxsplit=1)[0].lower().startswith("/stats"))
async def cmd_stats(message: Message) -> None:
    if not message.from_user or message.from_user.id not in ADMIN_IDS:
        await message.answer("Тільки для адміністраторів.")
        return

    users = get_all_registered_users()
    total = len(users)
    unbanned = len(get_unbanned_registered_users())
    banned = total - unbanned
    await message.answer(
        (
            f"Статистика бота:\n"
            f"Зареєстровані користувачі: {total}\n"
            f"Незаблоковані користувачі: {unbanned}\n"
            f"Заблоковані користувачі: {banned}"
        )
    )
