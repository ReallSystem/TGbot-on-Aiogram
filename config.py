
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from the .env file.
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise ValueError("BOT_TOKEN не встановлений в .env файлі")

# Read administrator IDs from the environment as a comma-separated list.
admin_ids_str = os.getenv("ADMIN_IDS", "").strip()
if not admin_ids_str:
    raise ValueError("ADMIN_IDS не встановлений у .env файлі")

try:
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
except ValueError:
    raise ValueError("ADMIN_IDS повинен містити цифри, розділені комами")

if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS містить невалідні значення")

# Database URL (автоматично встановлюється Railway для PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("⚠️ DATABASE_URL не встановлена! Перевірте налаштування Railway або .env файл")
    logger.info("🗂️ На Railway базу автоматично створюють у plugin'ах PostgreSQL")

logger.info(f"✅ Конфігурація завантажена. Admin IDs: {len(ADMIN_IDS)}")
logger.info(f"🗄️ Database: {DATABASE_URL[:20]}..." if DATABASE_URL else "Database: не встановлена")
