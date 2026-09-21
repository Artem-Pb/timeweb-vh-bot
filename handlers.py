import aiohttp
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keybords import get_start_keyboard, get_back_keyboard
from service import check_balance, check_domains, check_sites
from exeptions import TimewebApiError, TimewebDomainsNotFound, TimewebSiteIsNotFound

logger = logging.getLogger(__name__)
user_router = Router()

NETWORK_ERROR_TEXT = "Сервер временно недоступен, попробуйте позже"


async def _handle_api_call(callback: CallbackQuery, http_session: aiohttp.ClientSession,
                            fetch, format_result, error_messages: dict) -> None:
    try:
        result = await fetch(http_session)
    except tuple(error_messages) as e:
        await callback.message.edit_text(error_messages[type(e)], reply_markup=get_back_keyboard())
    else:
        await callback.message.edit_text(format_result(result), reply_markup=get_back_keyboard())


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
    await _handle_api_call(
        callback, http_session, check_balance,
        format_result=lambda result: f"Ваш баланс = {result.get('balance')}",
        error_messages={
            TimewebApiError: "Не удалось получить баланс — сервер ответил с ошибкой",
            aiohttp.ClientError: NETWORK_ERROR_TEXT,
        },
    )


@user_router.callback_query(F.data == "domain")
async def domains(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer("Какие же там домены...")
    await _handle_api_call(
        callback, http_session, check_domains,
        format_result=lambda result: "\n".join(result),
        error_messages={
            TimewebDomainsNotFound: "Нет доменов",
            TimewebApiError: "Не удалось получить домены - сервер ответил с ошибкой",
            aiohttp.ClientError: NETWORK_ERROR_TEXT,
        },
    )


@user_router.callback_query(F.data == "sites")
async def sites(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer()
    await _handle_api_call(
        callback, http_session, check_sites,
        format_result=lambda result: "\n".join(result),
        error_messages={
            TimewebSiteIsNotFound: "Нет сайтов",
            TimewebApiError: "Не удалось получить сайты - сервер ответил ошибкой",
            aiohttp.ClientError: NETWORK_ERROR_TEXT,
        },
    )

@user_router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Welcome to home!",
        reply_markup=get_start_keyboard()
    )
