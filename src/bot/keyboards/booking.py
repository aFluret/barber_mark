"""
/**
 * @file: booking.py
 * @description: Inline-клавиатуры сценария записи (дата/время/подтверждение)
 * @dependencies: aiogram.types
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def date_picker_keyboard(dates: list[date]) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for d in dates:
        buttons.append(
            [InlineKeyboardButton(text=d.strftime("%d.%m"), callback_data=f"bk_date:{d.isoformat()}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_picker_keyboard(slots: list[str]) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for slot in slots:
        buttons.append(
            [InlineKeyboardButton(text=slot, callback_data=f"bk_time:{slot}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_booking_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="bk_confirm:1")],
            [InlineKeyboardButton(text="❌ Назад", callback_data="bk_confirm:0")],
        ]
    )
