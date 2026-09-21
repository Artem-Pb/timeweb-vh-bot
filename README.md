# Бот для работы с API Timeweb Hosting

Простой Telegram-бот, который обращается к API Timeweb Hosting и предоставляет данные из аккаунта пользователя по запросу:

- баланс;
- список доменов;
- список сайтов.

## Требования

- Python 3.10
- aiogram 3.31.0
- aiohttp 3.14.3
- и т. д.

Полный список зависимостей указан в файле [requirements.txt](requirements.txt).

## Установка

```bash
git clone <ссылка>
cd timeweb-vh-bot
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка окружения

Переменные в файле `.env.example` представлены без значений. Перед запуском необходимо создать файл `.env`, перенести в него переменные из `.env.example` и заполнить их нужными значениями.

| Переменная   | Способ получения |
| ------------ | ---------------- |
| `BOT_TOKEN`  | Перейти в [BotFather](https://t.me/BotFather), создать бота и получить его токен вида `1234567890:AAEExampleFakeTokenNotReal12345` |
| `TW_API_KEY` | Получить ключ через поддержку [Timeweb.Hosting](https://hosting.timeweb.ru/support/help/other-question). Ключ имеет вид: `a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6` |
| `TOKEN`      | Получить с помощью [API-запроса](#получение-token), используя `TW_API_KEY`, логин и пароль аккаунта [Timeweb.Hosting](https://hosting.timeweb.ru/login). ключ имеет вид: `a1b2c3d4-11111111111111-e5f6a7b8c9d0` |
| `LOGIN`      | Логин аккаунта Timeweb.Hosting, к которому подключается бот |

### Получение TOKEN

```bash
curl -X POST "https://api.timeweb.ru/v1.2/access" \
  -H "accept: application/json" \
  -H "x-app-key: TW_API_KEY" \
  -u {login}:{password}
````

