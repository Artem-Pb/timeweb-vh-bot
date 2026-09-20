import config
from enum import Enum

class ApiEndpoint(Enum):
    URL_FOR_BALANCE = f"https://api.timeweb.ru/v1.1/finances/accounts/{config.LOGIN}"
    URL_FOR_SITE = f"https://api.timeweb.ru/v1.1/sites/{config.LOGIN}"
    HEADERS = {
        "Accept": "application/json",
        "x-app-key": f"{config.API_KEY}",
        "Authorization": f"Bearer {config.TOKEN}"
    }


class LogTexts(Enum):
    CHECK_STATUS_API = "Проверка API HTTP -> "
    API_NOT_FOUND = "API сейчас недоступен: "
    CODE = "Код ошибки: "
    ANSWER = "Ответ: "
    SITE_IS_NOT_AVAILABLE = "Ошибка сети: сайт недоступен"