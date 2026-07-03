"""
Rate Limiting для БД - обмеження дій користувача
Запобігає спаму та перевантаженню сервера
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from db.models import User, UserAction

logger = logging.getLogger(__name__)

# Константи ліміту
RATE_LIMITS = {
    "messages": {
        "max_count": 50,      # максимум 50 повідомлень
        "window_seconds": 60  # за 60 секунд (1 хвилина)
    },
    "button_click": {
        "max_count": 30,
        "window_seconds": 60
    },
    "command": {
        "max_count": 20,
        "window_seconds": 60
    }
}


def check_rate_limit(db: Session, user_id: int, action_type: str = "messages") -> tuple[bool, str]:
    """
    Перевірити, чи користувач перевищив ліміт дій

    Args:
        db: Сесія БД
        user_id: ID користувача
        action_type: тип дії (messages, button_click, command)

    Returns:
        (дозволено, повідомлення помилки)
    """
    try:
        if action_type not in RATE_LIMITS:
            return True, ""

        limit_config = RATE_LIMITS[action_type]
        max_count = limit_config["max_count"]
        window_seconds = limit_config["window_seconds"]

        # Час, раніше за який не рахуємо дії
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)

        # Залежно від типу дії рахуємо по-різному
        if action_type == "messages":
            # Рахуємо повідомлення за останні N секунд
            from db.models import ChatMessage
            count = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.user_id == user_id,
                    ChatMessage.created_at > cutoff_time
                )
            ).count()

        else:
            # Рахуємо дії за останні N секунд
            count = db.query(UserAction).filter(
                and_(
                    UserAction.user_id == user_id,
                    UserAction.action_type == action_type,
                    UserAction.updated_at > cutoff_time
                )
            ).count()

        if count >= max_count:
            remaining_time = int((datetime.now() - (cutoff_time + timedelta(seconds=window_seconds))).total_seconds())
            if remaining_time < 0:
                remaining_time = 0

            error_msg = (
                f"⏱️ Занадто багато дій! "
                f"Почекайте {remaining_time + window_seconds} сек. ({count}/{max_count})"
            )
            logger.warning(f"Rate limit exceeded for user {user_id}, action: {action_type}")
            return False, error_msg

        return True, ""

    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        # Якщо помилка - дозволяємо дію (краще дозволити, ніж заблокувати)
        return True, ""


def get_user_action_count(db: Session, user_id: int, action_type: str, window_seconds: int = 60) -> int:
    """
    Отримати кількість дій користувача за останні N секунд

    Args:
        db: Сесія БД
        user_id: ID користувача
        action_type: тип дії
        window_seconds: вікно часу в секундах

    Returns:
        Кількість дій
    """
    try:
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)

        count = db.query(UserAction).filter(
            and_(
                UserAction.user_id == user_id,
                UserAction.action_type == action_type,
                UserAction.updated_at > cutoff_time
            )
        ).count()

        return count
    except Exception as e:
        logger.error(f"Error getting action count: {e}")
        return 0


def get_rate_limit_status(db: Session, user_id: int) -> dict:
    """
    Отримати статус усіх лімітів для користувача

    Returns:
        {
            "messages": {"current": 5, "max": 50, "remaining": 45},
            "button_click": {"current": 2, "max": 30, "remaining": 28},
            ...
        }
    """
    try:
        status = {}

        for action_type, config in RATE_LIMITS.items():
            current = get_user_action_count(
                db, user_id, action_type,
                window_seconds=config["window_seconds"]
            )
            max_count = config["max_count"]
            remaining = max(0, max_count - current)

            status[action_type] = {
                "current": current,
                "max": max_count,
                "remaining": remaining,
                "limited": current >= max_count
            }

        return status
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return {}


def get_most_active_users(db: Session, limit: int = 10, window_minutes: int = 60) -> list:
    """
    Отримати найактивніших користувачів за останній час

    Returns список (user_id, action_count)
    """
    try:
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)

        from sqlalchemy import func
        active_users = db.query(
            UserAction.user_id,
            func.sum(UserAction.count).label("total_actions")
        ).filter(
            UserAction.updated_at > cutoff_time
        ).group_by(
            UserAction.user_id
        ).order_by(
            func.sum(UserAction.count).desc()
        ).limit(limit).all()

        return active_users
    except Exception as e:
        logger.error(f"Error getting most active users: {e}")
        return []
