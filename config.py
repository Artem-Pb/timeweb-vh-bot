import os
from dotenv import load_dotenv

load_dotenv(".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("TW_API_KEY")
TOKEN = os.getenv("TOKEN")
LOGIN = os.getenv("LOGIN")
PROXY_URL = os.getenv("PROXY_URL")