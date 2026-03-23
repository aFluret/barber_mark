"""
/**
 * @file: admin.py
 * @description: Админ-команды просмотра записей (MVP)
 * @dependencies: infra.db.repositories, infra.config.settings
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from datetime import date, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.infra.config.settings import get_settings
from src.infra.db.repositories.appointments_repository import AppointmentsRepository
from src.infra.db.repositories.users_repository import UsersRepository

router = Router()
appointments_repo = AppointmentsRepository()
users_repo = UsersRepository()


def _is_admin(user_id: int) -> bool:
    settings = get_settings()
    raw = settings.admin_user_ids.strip()
    if not raw:
        return False
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            ids.append(int(part))
    return user_id in ids


def _format_line(time_slot: str, name: str, phone: str) -> str:
    return f"{time_slot} — {name} ({phone})"


async def _send_for_date(message: Message, target_date: date) -> None:
    appts = await appointments_repo.list_by_date_from_today(target_date)
    if not appts:
        await message.answer("Записей нет.")
        return

    lines: list[str] = []
    # N+1 — допустимо для MVP.
    for appt in appts:
        user = await users_repo.get_by_user_id(appt.user_id)
        if user is None:
            continue
        lines.append(
            _format_line(
                time_slot=appt.time_slot.strftime("%H:%M"),
                name=user.name,
                phone=user.phone,
            )
        )

    await message.answer("\n".join(lines) if lines else "Записей нет.")


@router.message(Command("today"))
async def today_appointments(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Недостаточно прав.")
        return
    await _send_for_date(message, date.today())


@router.message(Command("tomorrow"))
async def tomorrow_appointments(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Недостаточно прав.")
        return
    await _send_for_date(message, date.today() + timedelta(days=1))


@router.message(Command("all"))
async def all_future_appointments(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("Недостаточно прав.")
        return

    appts = await appointments_repo.list_confirmed_from_date(date.today())
    if not appts:
        await message.answer("Будущих записей нет.")
        return

    lines: list[str] = []
    for appt in appts:
        user = await users_repo.get_by_user_id(appt.user_id)
        if user is None:
            continue
        lines.append(
            _format_line(
                time_slot=appt.time_slot.strftime("%H:%M"),
                name=user.name,
                phone=user.phone,
            )
        )

    await message.answer("\n".join(lines) if lines else "Будущих записей нет.")
