
import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
if not TOKEN:
    raise ValueError("BOT_TOKEN не встановлений в .env файлі")

# Read administrator IDs from the environment as a comma-separated list.
ADMIN_IDS = list(
    map(
        int,
        os.getenv("ADMIN_IDS", "").split(","),
    )
)
if not ADMIN_IDS or ADMIN_IDS == [0]:
    raise ValueError("ADMIN_IDS не встановлений або має неправильний формат у .env файлі")
