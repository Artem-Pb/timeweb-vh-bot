from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import UserTexts

def get_start_keyboard() -> InlineKeyboardMarkup:
    inl = InlineKeyboardBuilder()
    inl.add(
        InlineKeyboardButton(
            text=UserTexts.BTN_DOMAINS.value,
            callback_data="domain"),
        InlineKeyboardButton(
            text=UserTexts.BTN_SITES.value,
            callback_data="sites"),
        InlineKeyboardButton(
            text=UserTexts.BTN_BALANCE.value,
            callback_data="balance"),
    )

    inl.adjust(1, 1, 1)
    return inl.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    inl = InlineKeyboardBuilder()
    inl.add(
        InlineKeyboardButton(
            text=UserTexts.BTN_BACK.value,
            callback_data="back"
        )
    )
    inl.adjust(1)
    return inl.as_markup()


