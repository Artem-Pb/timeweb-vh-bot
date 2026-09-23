import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv(".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("TW_API_KEY")
TOKEN = os.getenv("TOKEN")
LOGIN = os.getenv("LOGIN")
PROXY_URL = os.getenv("PROXY_URL")

if not API_KEY:
    logger.warning("API_KEY не установлен, обратитесь в поддержку timeweb.hosting")

if not TOKEN:
    logger.warning("TOKEN - не установлен, необходимо авторизоваться по инструкции timeweb.hosting")

if not LOGIN:
    logger.warning("LOGIN неизвестен, обратитесь в панель управления timeweb.hosting")

if not PROXY_URL:
    logger.info("Прокси не установлен")
else:
    logger.info("Прокси установлен")