"""
/**
 * @file: schedule_service.py
 * @description: Сервис генерации временных слотов (пока на дефолтном графике)
 * @dependencies: datetime, typing
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from datetime import date, datetime, timedelta


class ScheduleService:
    # Дефолтный график для MVP foundation.
    # В следующих шагах график будет приходить из БД (таблицы work_schedule/исключения).
    DEFAULT_START = "10:00"
    DEFAULT_END = "18:00"
    DEFAULT_STEP_MINUTES = 30
    WORKING_WEEKDAYS = {0, 1, 2, 3, 4, 5}  # Пн..Сб (0=Пн)

    def generate_slots(self, start: str, end: str, step_minutes: int) -> list[str]:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        slots: list[str] = []
        current = start_dt
        while current < end_dt:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=step_minutes)
        return slots

    def is_working_day(self, target_date: date) -> bool:
        return target_date.weekday() in self.WORKING_WEEKDAYS

    def get_candidate_slots_for_date(self, target_date: date) -> list[str]:
        if not self.is_working_day(target_date):
            return []
        return self.generate_slots(
            self.DEFAULT_START, self.DEFAULT_END, self.DEFAULT_STEP_MINUTES
        )
