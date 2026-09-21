from enum import Enum

class LogTexts(Enum):
    CHECK_STATUS_API = "Проверка API HTTP -> "
    API_NOT_FOUND = "API сейчас недоступен: "
    CODE = "Код ошибки: "
    ANSWER = "Ответ: "
    SITE_IS_NOT_AVAILABLE = "Ошибка сети: сайт недоступен"