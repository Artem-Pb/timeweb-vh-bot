import asyncio
import sys

import aiohttp
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import text as sql_text
from sqlalchemy.exc import SQLAlchemyError

import config
import db
import service
from exeptions import TimewebAuthError

REQUIRED_VARS = {
    "BOT_TOKEN": config.BOT_TOKEN,
    "TW_API_KEY": config.API_KEY,
    "POSTGRESQL_HOST": config.POSTGRESQL_HOST,
    "POSTGRESQL_PORT": config.POSTGRESQL_PORT,
    "POSTGRESQL_USER": config.POSTGRESQL_USER,
    "POSTGRESQL_PASSWORD": config.POSTGRESQL_PASSWORD,
    "POSTGRESQL_DBNAME": config.POSTGRESQL_DBNAME,
}


def _report(title: str, ok: bool, detail: str = "") -> None:
    status = "OK" if ok else "FAIL"
    line = f"[{status}] {title}"
    if detail:
        line += f" -- {detail}"
    print(line)


def check_python_version() -> bool:
    ok = sys.version_info >= (3, 10)
    _report("Python >= 3.10", ok, sys.version.split()[0])
    return ok


def check_required_vars() -> bool:
    missing = [name for name, value in REQUIRED_VARS.items() if not value]
    ok = not missing
    _report("Обязательные переменные .env заполнены", ok, f"пусто: {', '.join(missing)}" if missing else "")
    return ok


async def check_telegram() -> bool:
    via = "через PROXY_URL" if config.PROXY_URL else "напрямую"
    title = f"Telegram Bot API ({via})"
    session = AiohttpSession(proxy=config.PROXY_URL) if config.PROXY_URL else None
    bot = Bot(token=config.BOT_TOKEN, session=session)
    try:
        me = await bot.get_me(request_timeout=10)
        _report(title, True, f"доступен, @{me.username}")
        return True
    except TelegramAPIError as e:
        _report(title, False, str(e))
        return False
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
        hint = "" if config.PROXY_URL else " -- если Telegram блокируется в этом регионе, задай PROXY_URL в .env"
        _report(title, False, f"{e}{hint}")
        return False
    finally:
        await bot.session.close()


async def check_timeweb() -> bool:
    title = "Timeweb API (сетевая доступность)"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            await service.login(session, "check-env-probe", "check-env-probe")
            _report(title, True, "сервер ответил")
            return True
        except TimewebAuthError:
            _report(title, True, "сервер ответил (заведомо неверные тестовые креды отклонены — хост доступен)")
            return True
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            hint = "" if config.PROXY_URL else " -- возможна блокировка на уровне хостинга"
            _report(title, False, f"{e}{hint}")
            return False


async def check_database() -> bool:
    title = "PostgreSQL"
    try:
        async with db.get_engine().connect() as conn:
            await conn.execute(sql_text("SELECT 1"))
        _report(title, True, "подключение установлено")
        return True
    except SQLAlchemyError as e:
        _report(title, False, str(e))
        return False


async def main() -> None:
    print("Проверка окружения перед запуском бота\n")

    results = [check_python_version(), check_required_vars()]
    results.append(await check_telegram())
    results.append(await check_timeweb())
    results.append(await check_database())

    print()
    if all(results):
        print("Окружение готово, можно запускать: .venv/bin/python3 main.py")
    else:
        print("Есть проблемы (см. FAIL выше) -- бот может не запуститься как есть.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
