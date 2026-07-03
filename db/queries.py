"""
Функції для роботи з БД
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from db.models import User, ChatMessage, UserAction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Константи безпеки
MAX_TEXT_LENGTH = 4096
MAX_USERNAME_LENGTH = 32
MAX_NAME_LENGTH = 256
MAX_ACTION_NAME_LENGTH = 256


# ===== КОРИСТУВАЧІ =====

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Отримати користувача або створити нового"""
    try:
        # Валідація входу
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            logger.warning(f"Invalid telegram_id: {telegram_id}")
            return None
        
        if username:
            username = username[:MAX_USERNAME_LENGTH]
        if first_name:
            first_name = first_name[:MAX_NAME_LENGTH]
        if last_name:
            last_name = last_name[:MAX_NAME_LENGTH]
        
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Оновити дані якщо змінилися
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.updated_at = datetime.now()
            db.commit()
            db.refresh(user)
        
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_or_create_user: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_or_create_user: {e}")
        return None


def get_user(db: Session, telegram_id: int):
    """Отримати користувача за telegram_id"""
    try:
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return None
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user: {e}")
        return None


def get_all_users(db: Session):
    """Отримати всіх користувачів"""
    try:
        return db.query(User).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all_users: {e}")
        return []


def get_user_count(db: Session):
    """Отримати кількість користувачів"""
    try:
        return db.query(func.count(User.id)).scalar() or 0
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_count: {e}")
        return 0
def get_user_count(db: Session):
    """Отримати кількість користувачів"""
    return db.query(func.count(User.id)).scalar()


# ===== ПОВІДОМЛЕННЯ =====

def add_message(db: Session, user_id: int, text: str, message_type: str = "text", telegram_message_id: int = None):
    """Додати повідомлення в історію чату"""
    try:
        # Валідація входу
        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id: {user_id}")
            return None
        
        if not isinstance(text, str) or len(text) == 0:
            logger.warning(f"Invalid text provided")
            return None
        
        # Обрізати дуже довгий текст
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {MAX_TEXT_LENGTH}")
            text = text[:MAX_TEXT_LENGTH]
        
        message = ChatMessage(
            user_id=user_id,
            text=text,
            message_type=message_type[:50],  # Обмеження типу повідомлення
            telegram_message_id=telegram_message_id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    except SQLAlchemyError as e:
        logger.error(f"Database error in add_message: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error in add_message: {e}")
        return None


def get_user_messages(db: Session, user_id: int, limit: int = 50):
    """Отримати останні повідомлення користувача"""
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            return []
        
        # Безпечний ліміт
        limit = min(max(1, limit), 500)
        
        return db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_messages: {e}")
        return []


def get_message_count(db: Session, user_id: int = None):
    """Отримати кількість повідомлень"""
    try:
        query = db.query(func.count(ChatMessage.id))
        if user_id:
            if not isinstance(user_id, int) or user_id <= 0:
                return 0
            query = query.filter(ChatMessage.user_id == user_id)
        return query.scalar() or 0
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_message_count: {e}")
        return 0


# ===== ДІЇ КОРИСТУВАЧА =====

def log_action(db: Session, user_id: int, action_type: str, action_name: str):
    """Записати дію користувача (клік на кнопку)"""
    try:
        # Валідація входу
        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id: {user_id}")
            return None
        
        if not isinstance(action_type, str) or len(action_type) == 0:
            logger.warning(f"Invalid action_type")
            return None
        
        if not isinstance(action_name, str) or len(action_name) == 0:
            logger.warning(f"Invalid action_name")
            return None
        
        # Обрізати довгі значення
        action_type = action_type[:100]
        action_name = action_name[:MAX_ACTION_NAME_LENGTH]
        
        action = db.query(UserAction).filter(
            UserAction.user_id == user_id,
            UserAction.action_type == action_type,
            UserAction.action_name == action_name
        ).first()

        if action:
            action.count += 1
            action.updated_at = datetime.now()
        else:
            action = UserAction(
                user_id=user_id,
                action_type=action_type,
                action_name=action_name,
                count=1
            )
            db.add(action)

        db.commit()
        db.refresh(action)
        return action
    except SQLAlchemyError as e:
        logger.error(f"Database error in log_action: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error in log_action: {e}")
        return None


def get_top_actions(db: Session, limit: int = 10, action_type: str = None):
    """Отримати топ популярних дій"""
    try:
        # Безпечний ліміт
        limit = min(max(1, limit), 1000)
        
        query = db.query(UserAction).order_by(UserAction.count.desc())
        if action_type:
            action_type = action_type[:100]
            query = query.filter(UserAction.action_type == action_type)
        return query.limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_top_actions: {e}")
        return []


def get_user_top_actions(db: Session, user_id: int, limit: int = 10):
    """Отримати топ дій конкретного користувача"""
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            return []
        
        limit = min(max(1, limit), 500)
        
        return db.query(UserAction).filter(
            UserAction.user_id == user_id
        ).order_by(UserAction.count.desc()).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_top_actions: {e}")
        return []


# ===== СТАТИСТИКА =====

def get_statistics(db: Session):
    """Отримати загальну статистику"""
    try:
        total_actions = db.query(func.sum(UserAction.count)).scalar() or 0
        return {
            "total_users": get_user_count(db),
            "total_messages": get_message_count(db),
            "total_actions": total_actions
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_statistics: {e}")
        return {
            "total_users": 0,
            "total_messages": 0,
            "total_actions": 0
        }
