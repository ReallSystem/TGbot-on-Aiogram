import logging
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS
from handlers.user import (
    ban_user,
    get_unbanned_registered_users,
    unban_user,
)

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


def is_admin(user_id: int) -> bool:
    """Check if the sender is listed as an administrator."""
    return user_id in ADMIN_IDS


@router.message(Command("ban"))
async def cmd_ban(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return

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


@router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return

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


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return

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
