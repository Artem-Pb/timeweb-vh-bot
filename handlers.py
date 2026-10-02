import aiohttp
import logging
import functools
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

import repository
import texts
from keybords import get_start_keyboard, get_back_keyboard
from models import User
from service import check_balance, check_domains, check_sites, login as tw_login
from states import AuthStates
from exeptions import TimewebApiError, TimewebDomainsNotFound, TimewebSiteIsNotFound, TimewebAuthError
from texts import UserTexts

logger = logging.getLogger(__name__)
user_router = Router()

async def _save_edit(callback: CallbackQuery, text: str, keyboard) -> None:
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard)
    except TelegramBadRequest as e:
        if texts.LogTexts.TELEGRAM_BAD_REQUEST.value in str(e):
            pass
        else:
            raise

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
        text = error_messages[type(e)]
    else:
        text = format_result(result)
    await _save_edit(callback, text, get_back_keyboard())

async def _require_login(callback: CallbackQuery, db_session_factory: async_sessionmaker[AsyncSession]) -> User | None:
    async with db_session_factory() as db_session:
        user = await repository.get_user(db_session, callback.from_user.id)
    if user is None:
        await _save_edit(callback, UserTexts.NOT_LOGGED_IN.value, get_start_keyboard())
    return user

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


@user_router.message(Command("login"))
@log_action
async def login_start(message: Message, state: FSMContext):
    await message.answer(UserTexts.LOGIN_ASK_LOGIN.value)
    await state.set_state(AuthStates.waiting_login)


@user_router.message(AuthStates.waiting_login)
async def login_got_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer(UserTexts.LOGIN_ASK_PASSWORD.value)
    await state.set_state(AuthStates.waiting_password)


@user_router.message(AuthStates.waiting_password)
async def login_got_password(message: Message, state: FSMContext, http_session: aiohttp.ClientSession,
                              db_session_factory: async_sessionmaker[AsyncSession]):
    data = await state.get_data()
    login_value = data["login"]
    password = message.text

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    try:
        token = await tw_login(http_session, login_value, password)
    except (TimewebAuthError, TimewebApiError, aiohttp.ClientError):
        await message.answer(UserTexts.LOGIN_FAILED.value)
        await state.clear()
        return

    async with db_session_factory() as db_session:
        await repository.save_user(db_session, message.from_user.id, login_value, token)

    await state.clear()
    await message.answer(UserTexts.LOGIN_SUCCESS.value, reply_markup=get_start_keyboard())


@user_router.callback_query(F.data == "balance")
@log_action
async def balance(callback: CallbackQuery, http_session: aiohttp.ClientSession,
                   db_session_factory: async_sessionmaker[AsyncSession]):
    user = await _require_login(callback, db_session_factory)
    if user is None:
        return
    await callback.answer(UserTexts.BALANCE_LOADING.value)
    await _handle_api_call(
        callback, http_session,
        fetch=lambda session: check_balance(session, user.tw_login, user.tw_token),
        format_result=lambda result: UserTexts.BALANCE_RESULT.value.format(value=result.get("balance")),
        error_messages={
            TimewebApiError: UserTexts.BALANCE_ERROR.value,
            TimewebAuthError: UserTexts.AUTH_ERROR.value,
            aiohttp.ClientError: UserTexts.NETWORK_ERROR.value,
        },
    )


@user_router.callback_query(F.data == "domain")
@log_action
async def domains(callback: CallbackQuery, http_session: aiohttp.ClientSession,
                   db_session_factory: async_sessionmaker[AsyncSession]):
    user = await _require_login(callback, db_session_factory)
    if user is None:
        return
    await callback.answer(UserTexts.DOMAINS_LOADING.value)
    await _handle_api_call(
        callback, http_session,
        fetch=lambda session: check_domains(session, user.tw_login, user.tw_token),
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
async def sites(callback: CallbackQuery, http_session: aiohttp.ClientSession,
                 db_session_factory: async_sessionmaker[AsyncSession]):
    user = await _require_login(callback, db_session_factory)
    if user is None:
        return
    await callback.answer(UserTexts.SITES_LOADING.value)
    await _handle_api_call(
        callback, http_session,
        fetch=lambda session: check_sites(session, user.tw_login, user.tw_token),
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
    await _save_edit(callback, UserTexts.START.value, get_start_keyboard())
