"""
/**
 * @file: appointment.py
 * @description: Просмотр и отмена активной записи пользователя
 * @dependencies: app.services.booking_service, bot.keyboards.main_menu, fsm
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.app.services.booking_service import BookingService
from src.bot.keyboards.main_menu import main_menu_keyboard

router = Router()
booking_service = BookingService()


@router.message(F.text == "📋 Моя запись")
async def my_appointment(message: Message) -> None:
    user_id = message.from_user.id
    appt = await booking_service.get_active_appointment(user_id)
    if appt is None:
        await message.answer("У вас пока нет активной записи.", reply_markup=main_menu_keyboard())
        return

    await message.answer(
        f"Ваша запись:\n{appt.date.strftime('%d.%m.%Y')} в {appt.time_slot.strftime('%H:%M')}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "❌ Отменить запись")
async def cancel_appointment(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.clear()

    appt = await booking_service.cancel_active_appointment(user_id)
    if appt is None:
        await message.answer("Активной записи не найдено.", reply_markup=main_menu_keyboard())
        return

    await message.answer(
        "Запись отменена. Слот снова доступен.",
        reply_markup=main_menu_keyboard(),
    )
