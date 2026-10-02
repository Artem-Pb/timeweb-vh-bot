import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv(".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("TW_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")

POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_DBNAME = os.getenv("POSTGRESQL_DBNAME")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}"
    f"@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DBNAME}"
)

if not API_KEY:
    logger.warning("API_KEY не установлен, обратитесь в поддержку timeweb.hosting")

if not PROXY_URL:
    logger.info("Прокси не установлен")
else:
    logger.info("Прокси установлен")

for name, value in {
    "POSTGRESQL_HOST": POSTGRESQL_HOST,
    "POSTGRESQL_PORT": POSTGRESQL_PORT,
    "POSTGRESQL_USER": POSTGRESQL_USER,
    "POSTGRESQL_PASSWORD": POSTGRESQL_PASSWORD,
    "POSTGRESQL_DBNAME": POSTGRESQL_DBNAME,
}.items():
    if not value:
        logger.warning(f"{name} не установлен — подключение к БД не настроено")