from enum import Enum

class UserTexts(Enum):
    START = (
        "Здорова, я ботянский! Помогу тебе по работе с аккаунтом Timeweb.\n\n"
        "Жми на кнопку — покажу баланс, список доменов или список сайтов на аккаунте."
    )
    BALANCE_LOADING = "Считаем денежки..."
    DOMAINS_LOADING = "Какие же там домены..."
    SITES_LOADING = "Гляну, какие сайты у тебя есть..."
    BALANCE_RESULT = "Твой баланс: {value}"
    DOMAINS_RESULT = "Твои домены ({count}):\n\n{items}"
    SITES_RESULT = "Твои сайты ({count}):\n\n{items}"
    DOMAINS_EMPTY = "Доменов пока нет"
    SITES_EMPTY = "Сайтов пока нет"
    BALANCE_ERROR = "Не удалось получить баланс — сервер ответил с ошибкой"
    DOMAINS_ERROR = "Не удалось получить домены — сервер ответил с ошибкой"
    SITES_ERROR = "Не удалось получить сайты — сервер ответил с ошибкой"
    NETWORK_ERROR = "Сервер временно недоступен, попробуй чуть позже"
    BTN_BALANCE = "Баланс"
    BTN_DOMAINS = "Домены"
    BTN_SITES = "Сайты"
    BTN_BACK = "Домой/назад"


class LogTexts(Enum):
    CHECK_STATUS_API = "Проверка API HTTP -> "
    API_NOT_FOUND = "API сейчас недоступен: "
    CODE = "Код ошибки: "
    ANSWER = "Ответ: "
    SITE_IS_NOT_AVAILABLE = "Ошибка сети: сайт недоступен"