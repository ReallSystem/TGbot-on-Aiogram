from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class User(Base):
    """Модель користувача Telegram"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Зв'язки
    messages = relationship("ChatMessage", back_populates="user")
    actions = relationship("UserAction", back_populates="user")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class ChatMessage(Base):
    """Модель повідомлення в чаті"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    telegram_message_id = Column(Integer, nullable=True)
    text = Column(Text)
    message_type = Column(String, default="text")  # text, command, photo, etc.
    created_at = Column(DateTime, default=datetime.now)

    # Зв'язок
    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(user_id={self.user_id}, text={self.text[:50]})>"


class UserAction(Base):
    """Модель дій користувача (клік на кнопку)"""
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action_type = Column(String, index=True)  # button_click, command, etc.
    action_name = Column(String)  # назва кнопки або команди
    count = Column(Integer, default=1)  # кількість разів
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Зв'язок
    user = relationship("User", back_populates="actions")

    def __repr__(self):
        return f"<UserAction(user_id={self.user_id}, action={self.action_name}, count={self.count})>"
