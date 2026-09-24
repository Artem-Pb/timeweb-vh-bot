import aiohttp
import logging
import functools
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keybords import get_start_keyboard, get_back_keyboard
from service import check_balance, check_domains, check_sites
from exeptions import TimewebApiError, TimewebDomainsNotFound, TimewebSiteIsNotFound, TimewebAuthError
from texts import UserTexts

logger = logging.getLogger(__name__)
user_router = Router()

def log_action(original_funct):
    @functools.wraps(original_funct)
    async def wrapper_log(*args, **kwargs):
        event = args[0]
        user_id = event.from_user.id
        logger.info(f"{user_id}-> {original_funct.__name__}")
        result = await original_funct(*args, **kwargs)
        return result
    return wrapper_log

async def _handle_api_call(callback: CallbackQuery, http_session: aiohttp.ClientSession,
                            fetch, format_result, error_messages: dict) -> None:
    try:
        result = await fetch(http_session)
    except tuple(error_messages) as e:
        await callback.message.edit_text(error_messages[type(e)], reply_markup=get_back_keyboard())
    else:
        await callback.message.edit_text(format_result(result), reply_markup=get_back_keyboard())


def _format_domains(result: list[str]) -> str:
    items = "\n".join(f'• <a href="https://{escape(d)}">{escape(d)}</a>' for d in result)
    return UserTexts.DOMAINS_RESULT.value.format(count=len(result), items=items)


def _format_sites(result: list[str]) -> str:
    items = "\n".join(f"• {escape(s)}" for s in result)
    return UserTexts.SITES_RESULT.value.format(count=len(result), items=items)


@user_router.message(CommandStart())
@log_action
async def cmd_start(message: Message):
    await message.answer(
        UserTexts.START.value,
        reply_markup=get_start_keyboard()
    )


@user_router.callback_query(F.data == "balance")
@log_action
async def balance(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer(UserTexts.BALANCE_LOADING.value)
    await _handle_api_call(
        callback, http_session, check_balance,
        format_result=lambda result: UserTexts.BALANCE_RESULT.value.format(value=result.get("balance")),
        error_messages={
            TimewebApiError: UserTexts.BALANCE_ERROR.value,
            TimewebAuthError: UserTexts.AUTH_ERROR.value,
            aiohttp.ClientError: UserTexts.NETWORK_ERROR.value,
        },
    )


@user_router.callback_query(F.data == "domain")
@log_action
async def domains(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer(UserTexts.DOMAINS_LOADING.value)
    await _handle_api_call(
        callback, http_session, check_domains,
        format_result=_format_domains,
        error_messages={
            TimewebDomainsNotFound: UserTexts.DOMAINS_EMPTY.value,
            TimewebApiError: UserTexts.DOMAINS_ERROR.value,
            TimewebAuthError: UserTexts.AUTH_ERROR.value,
            aiohttp.ClientError: UserTexts.NETWORK_ERROR.value,
        },
    )


@user_router.callback_query(F.data == "sites")
@log_action
async def sites(callback: CallbackQuery, http_session: aiohttp.ClientSession):
    await callback.answer(UserTexts.SITES_LOADING.value)
    await _handle_api_call(
        callback, http_session, check_sites,
        format_result=_format_sites,
        error_messages={
            TimewebSiteIsNotFound: UserTexts.SITES_EMPTY.value,
            TimewebApiError: UserTexts.SITES_ERROR.value,
            TimewebAuthError: UserTexts.AUTH_ERROR.value,
            aiohttp.ClientError: UserTexts.NETWORK_ERROR.value,
        },
    )

@user_router.callback_query(F.data == "back")
@log_action
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text=UserTexts.START.value,
        reply_markup=get_start_keyboard()
    )
