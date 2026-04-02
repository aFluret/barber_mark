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

from src.infra.db.models import ServiceModel


def date_picker_keyboard(dates: list[date]) -> InlineKeyboardMarkup:
    # Показываем по 3 кнопки в ряду, чтобы уменьшить количество скролла.
    buttons: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(dates), 3):
        row = dates[i : i + 3]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=d.strftime("%d.%m"),
                    callback_data=f"bk_date:{d.isoformat()}",
                )
                for d in row
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def services_picker_keyboard(services: list[ServiceModel]) -> InlineKeyboardMarkup:
    """
    Инлайн-выбор услуги с отображением цены и длительности.
    callback_data формата: `bk_service:{service_id}`
    """

    buttons: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(services), 2):
        row = services[i : i + 2]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{s.name} — {s.price_byn} BYN ({s.duration_minutes} мин)",
                    callback_data=f"bk_service:{s.id}",
                )
                for s in row
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_picker_keyboard(slots: list[str]) -> InlineKeyboardMarkup:
    # Показываем по 3 кнопки в ряду.
    buttons: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(slots), 3):
        row = slots[i : i + 3]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=slot,
                    callback_data=f"bk_time:{slot}",
                )
                for slot in row
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_booking_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="bk_confirm:1")],
            [InlineKeyboardButton(text="❌ Назад", callback_data="bk_confirm:0")],
        ]
    )
