from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_keyboard() -> InlineKeyboardMarkup:
    inl = InlineKeyboardBuilder()
    inl.add(
        InlineKeyboardButton(
            text="Домены",
            callback_data="domain"),
        InlineKeyboardButton(
            text="Сайты",
            callback_data="sites"),
        InlineKeyboardButton(
            text="Баланс",
            callback_data="balance"),
    )

    inl.adjust(1, 1, 1)
    return inl.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    inl = InlineKeyboardBuilder()
    inl.add(
        InlineKeyboardButton(
            text="Домой/назад",
            callback_data="back"
        )
    )
    inl.adjust(1)
    return inl.as_markup()


