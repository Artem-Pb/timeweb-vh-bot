import aiohttp
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import exeptions
from keybords import get_start_keyboard, get_domains, get_sites, get_balance
from service import check_balance, check_domains, check_sites
from exeptions import TimewebApiError, TimewebDomainsNotFound, TimewebSiteIsNotFound

logger = logging.getLogger(__name__)
user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Здорова,я ботянский! помогу бе по работе с аккаунтом таймевеба. "
        "Могу тебе показать сколько денег и какие домены есть и какие есть сайты. "
        ,
        reply_markup=get_start_keyboard()
    )
    logger.info("Отправлен ответ человеку!")


@user_router.callback_query(F.data == "balance")
async def balance(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer("Считаем денежки...")
    try:
        result = await check_balance(http_session)
    except TimewebApiError:
        await callback.message.edit_text(
            "Не удалось получить баланс — сервер ответил с ошибкой",
            reply_markup=get_balance()
        )
    except aiohttp.ClientError:
        await callback.message.edit_text(
            "Сервер временно недоступен, попробуйте позже",
            reply_markup=get_balance()
        )
    else:
        balance_value = result.get("balance")
        await callback.message.edit_text(
            f"Ваш баланс = {balance_value}",
            reply_markup=get_balance()
        )


@user_router.callback_query(F.data == "domain")
async def domains(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer("Какие же там домены...")
    try:
        result = await check_domains(http_session)
    except TimewebDomainsNotFound:
        await callback.message.edit_text(
            "Нет доменов",
            reply_markup=get_domains()
        )
    except TimewebApiError:
        await callback.message.edit_text(
            "Не удалось получить домены - сервер ответил с ошибкой",
            reply_markup=get_domains()
        )
    except aiohttp.ClientError:
        await callback.message.edit_text(
            "Сервер временно недоступен, попробуйте позже",
            reply_markup=get_domains()
        )
    else:
        await callback.message.edit_text(
            "\n".join(result),
            reply_markup=get_domains()
        )

@user_router.callback_query(F.data == "sites")
async def sites(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer()
    try:
        result = await check_sites(http_session)
    except TimewebSiteIsNotFound:
        await callback.message.edit_text(
            "Нет сайтов",
            reply_markup=get_sites()
        )
    except TimewebApiError:
        await callback.message.edit_text(
            "Не удалось получить сайты - сервер ответил ошибкой",
            reply_markup=get_sites()
        )
    except aiohttp.ClientError:
        await callback.message.edit_text(
            "Сервер временно недоступен, попробуйте позже",
            reply_markup=get_sites()
        )
    else:
        await callback.message.edit_text(
            "\n".join(result),
            reply_markup=get_sites()
        )

@user_router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Welcome to home!",
        reply_markup=get_start_keyboard()
    )
