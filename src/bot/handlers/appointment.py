"""
/**
 * @file: appointment.py
 * @description: Просмотр и отмена активной записи пользователя
 * @dependencies: app.services.booking_service, bot.keyboards.main_menu, fsm
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from datetime import date, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.app.services.booking_service import BookingService
from src.bot.keyboards.main_menu import menu_keyboard_for_role

router = Router()
booking_service = BookingService()
RU_WEEKDAY_FULL = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}
RU_MONTHS_GEN = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def _human_booking_date(d: date) -> str:
    today = date.today()
    if d == today:
        suffix = "сегодня"
    elif d == today + timedelta(days=1):
        suffix = "завтра"
    else:
        suffix = RU_WEEKDAY_FULL[d.weekday()]
    return f"{d.day} {RU_MONTHS_GEN[d.month]} ({suffix})"


@router.message(F.text == "📋 Моя запись")
async def my_appointment(message: Message) -> None:
    user_id = message.from_user.id
    user = await booking_service.get_user(user_id)
    user_name = user.name if user and user.name else "Клиент"
    user_role = user.role if user else "client"
    appt = await booking_service.get_active_appointment(user_id)
    if appt is None:
        await message.answer(f"{user_name}, у тебя пока нет активной записи.", reply_markup=menu_keyboard_for_role(user_role))
        return

    await message.answer(
        f"{user_name}, ты записан на {_human_booking_date(appt.date)} ✅\n"
        f"Время: {appt.start_time.strftime('%H:%M')}–{appt.end_time.strftime('%H:%M')}",
        reply_markup=menu_keyboard_for_role(user_role),
    )


@router.message(F.text == "❌ Отменить запись")
async def cancel_appointment(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = await booking_service.get_user(user_id)
    user_name = user.name if user and user.name else "Клиент"
    user_role = user.role if user else "client"
    await state.clear()

    appt = await booking_service.cancel_active_appointment(user_id)
    if appt is None:
        await message.answer(f"{user_name}, активной записи не найдено.", reply_markup=menu_keyboard_for_role(user_role))
        return

    await message.answer(
        "Запись отменена ✅\n\nМожешь записаться заново на любую услугу.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Выбрать услугу", callback_data="bk_restart_service")]]
        ),
    )
