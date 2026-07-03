from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

# Для SQLite можна використовувати локальний файл
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot_database.db")

# Для SQLite потрібно переконатися, що це не файл у пам'яті
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Імпортуємо моделі, щоб вони зареєструвалися в Base
from .models import User, ChatMessage, UserAction


def init_db():
    """Створює всі таблиці в БД"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Отримати сесію БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
