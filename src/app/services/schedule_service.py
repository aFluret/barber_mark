"""
/**
 * @file: schedule_service.py
 * @description: Сервис генерации временных слотов (пока на дефолтном графике)
 * @dependencies: datetime, typing
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, time
from src.infra.db.repositories.work_schedule_repository import WorkScheduleModel, WorkScheduleRepository


class ScheduleService:
    DEFAULT_START = "10:00"
    DEFAULT_END = "18:00"
    # MVP: длительность визита фиксирована (шаг слота) 60 минут.
    DEFAULT_STEP_MINUTES = 60
    WORKING_WEEKDAYS = {0, 1, 2, 3, 4, 5}  # Пн..Сб (0=Пн)

    def __init__(self) -> None:
        self._repo = WorkScheduleRepository()

    def generate_slots(self, start: str, end: str, step_minutes: int) -> list[str]:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        slots: list[str] = []
        current = start_dt
        while current < end_dt:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=step_minutes)
        return slots

    @staticmethod
    def _time_to_hhmm(t: time) -> str:
        return t.strftime("%H:%M")

    async def _get_schedule_or_default(self) -> WorkScheduleModel:
        schedule = await self._repo.get_latest()
        if schedule is None:
            return WorkScheduleModel(
                weekdays=set(self.WORKING_WEEKDAYS),
                start_time=datetime.strptime(self.DEFAULT_START, "%H:%M").time(),
                end_time=datetime.strptime(self.DEFAULT_END, "%H:%M").time(),
            )
        return schedule

    async def next_working_dates(self, count: int) -> list[date]:
        today = date.today()
        schedule = await self._get_schedule_or_default()
        out: list[date] = []
        d = today
        while len(out) < count:
            if d.weekday() in schedule.weekdays:
                out.append(d)
            d += timedelta(days=1)
        return out

    async def get_candidate_slots_for_date(self, target_date: date) -> list[str]:
        schedule = await self._get_schedule_or_default()
        if target_date.weekday() not in schedule.weekdays:
            return []

        return self.generate_slots(
            self._time_to_hhmm(schedule.start_time),
            self._time_to_hhmm(schedule.end_time),
            self.DEFAULT_STEP_MINUTES,
        )
