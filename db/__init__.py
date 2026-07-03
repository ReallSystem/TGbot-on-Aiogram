from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger(__name__)

# Railway автоматично створює DATABASE_URL для PostgreSQL
# Формат: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL не встановлена у змінних оточення!")
    raise ValueError("DATABASE_URL environment variable is required")

# Для Railway PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # перевіряти з'єднання перед кожним використанням
    pool_recycle=3600,  # переcоздавать з'єднання кожну годину
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

# Імпортуємо моделі, щоб вони зареєструвалися в Base
from .models import User, ChatMessage, UserAction


def init_db():
    """Створює всі таблиці в БД"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def get_db():
    """Отримати сесію БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
