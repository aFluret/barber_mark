"""
/**
 * @file: main_menu.py
 * @description: Главное меню клиента
 * @dependencies: aiogram.types
 * @created: 2026-03-23
 */
"""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="📋 Моя запись")],
            [KeyboardButton(text="❌ Отменить запись")],
        ],
        resize_keyboard=True,
    )
