"""
/**
 * @file: work_schedule_repository.py
 * @description: Репозиторий рабочего графика для Supabase
 * @dependencies: infra.db.supabase_client, asyncio, datetime
 * @created: 2026-03-24
 */
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any, List, Optional, Set

from src.infra.db.supabase_client import get_supabase_client


@dataclass(frozen=True)
class WorkScheduleModel:
    weekdays: Set[int]  # python weekday: Пн=0 ... Вс=6
    start_time: time
    end_time: time
    lunch_time: Optional[time] = None


@dataclass(frozen=True)
class DayScheduleModel:
    is_day_off: bool
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None


@dataclass(frozen=True)
class MonthlyWorkScheduleModel:
    month: str  # YYYY-MM
    edit_mode: str  # full_month | by_weeks
    schedule_json: dict[str, Any]


class WorkScheduleRepository:
    async def get_latest(self) -> Optional[WorkScheduleModel]:
        def _op() -> Optional[dict]:
            client = get_supabase_client()
            # Новая схема: lunch_time. Делаем каскадный fallback для старых схем.
            try:
                res = (
                    client.table("work_schedule")
                    .select("weekdays,start_time,end_time,lunch_time,created_at")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
            except Exception:
                try:
                    res = (
                        client.table("work_schedule")
                        .select("weekdays,start_time,end_time,lunch_start,created_at")
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
                except Exception:
                    res = (
                        client.table("work_schedule")
                        .select("weekdays,start_time,end_time,created_at")
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
            return res.data[0] if res.data else None

        row = await asyncio.to_thread(_op)
        if not row:
            return None

        weekdays_raw = row.get("weekdays") or []
        weekdays: Set[int] = {int(x) for x in weekdays_raw}

        start_time_raw = row.get("start_time")
        end_time_raw = row.get("end_time")
        lunch_raw = row.get("lunch_time")
        if lunch_raw is None:
            lunch_raw = row.get("lunch_start")

        # Supabase time может приходить как строка "HH:MM:SS" или "HH:MM".
        start_s = str(start_time_raw)[:5]
        end_s = str(end_time_raw)[:5]
        start_t = datetime.strptime(start_s, "%H:%M").time()
        end_t = datetime.strptime(end_s, "%H:%M").time()
        lunch_t = datetime.strptime(str(lunch_raw)[:5], "%H:%M").time() if lunch_raw is not None else None

        return WorkScheduleModel(
            weekdays=weekdays,
            start_time=start_t,
            end_time=end_t,
            lunch_time=lunch_t,
        )

    async def set_schedule(
        self,
        weekdays: List[int],
        start_time: time,
        end_time: time,
        lunch_time: Optional[time] = None,
    ) -> None:
        payload = {
            "weekdays": list(weekdays),
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
        }
        payload_with_lunch = dict(payload)
        payload_with_lunch["lunch_time"] = lunch_time.strftime("%H:%M:%S") if lunch_time else None

        def _op() -> None:
            client = get_supabase_client()
            # Supabase/PostgREST требует WHERE для DELETE.
            # Обновляем последнюю запись, если она есть; иначе вставляем новую.
            latest = (
                client.table("work_schedule")
                .select("id")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            row = (latest.data or [None])[0]
            if row and row.get("id") is not None:
                try:
                    client.table("work_schedule").update(payload_with_lunch).eq("id", int(row["id"])).execute()
                except Exception:
                    client.table("work_schedule").update(payload).eq("id", int(row["id"])).execute()
            else:
                try:
                    client.table("work_schedule").insert(payload_with_lunch).execute()
                except Exception:
                    client.table("work_schedule").insert(payload).execute()

        await asyncio.to_thread(_op)

    @staticmethod
    def _parse_time(value: Any) -> Optional[time]:
        if value is None:
            return None
        raw = str(value).strip()
        if not raw:
            return None
        return datetime.strptime(raw[:5], "%H:%M").time()

    @staticmethod
    def _weekday_key(py_weekday: int) -> str:
        keys = {
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "saturday",
            6: "sunday",
        }
        return keys[py_weekday]

    async def get_month_schedule(self, month: str) -> Optional[MonthlyWorkScheduleModel]:
        def _op() -> Optional[dict[str, Any]]:
            client = get_supabase_client()
            res = (
                client.table("work_schedule_monthly")
                .select("month,edit_mode,schedule_json,updated_at")
                .eq("month", month)
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )
            return res.data[0] if res.data else None

        try:
            row = await asyncio.to_thread(_op)
        except Exception:
            # Таблица может отсутствовать до миграции.
            return None

        if not row:
            return None
        return MonthlyWorkScheduleModel(
            month=str(row.get("month") or month),
            edit_mode=str(row.get("edit_mode") or "full_month"),
            schedule_json=dict(row.get("schedule_json") or {}),
        )

    async def upsert_month_schedule(self, month: str, edit_mode: str, schedule_json: dict[str, Any]) -> None:
        payload = {
            "month": month,
            "edit_mode": edit_mode,
            "schedule_json": schedule_json,
            "updated_at": datetime.utcnow().isoformat(),
        }

        def _op() -> None:
            client = get_supabase_client()
            existing = (
                client.table("work_schedule_monthly")
                .select("id")
                .eq("month", month)
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )
            row = (existing.data or [None])[0]
            if row and row.get("id") is not None:
                client.table("work_schedule_monthly").update(payload).eq("id", int(row["id"])).execute()
            else:
                client.table("work_schedule_monthly").insert(payload).execute()

        await asyncio.to_thread(_op)

    async def get_day_schedule(self, target_date: date) -> Optional[DayScheduleModel]:
        month_key = target_date.strftime("%Y-%m")
        monthly = await self.get_month_schedule(month_key)
        if monthly is None:
            return None

        data = monthly.schedule_json or {}
        weekday_key = self._weekday_key(target_date.weekday())

        def _from_day_payload(day_payload: dict[str, Any]) -> DayScheduleModel:
            is_day_off = bool(day_payload.get("is_day_off"))
            start_t = self._parse_time(day_payload.get("start_time"))
            end_t = self._parse_time(day_payload.get("end_time"))
            lunch_start = self._parse_time(day_payload.get("lunch_start"))
            lunch_end = self._parse_time(day_payload.get("lunch_end"))
            if is_day_off:
                return DayScheduleModel(is_day_off=True)
            return DayScheduleModel(
                is_day_off=False,
                start_time=start_t,
                end_time=end_t,
                lunch_start=lunch_start,
                lunch_end=lunch_end,
            )

        if monthly.edit_mode == "full_month":
            days_of_week = data.get("days_of_week") or {}
            payload = days_of_week.get(weekday_key)
            if not isinstance(payload, dict):
                return None
            return _from_day_payload(payload)

        weeks = data.get("weeks") or []
        iso_target = target_date.isoformat()
        for week in weeks:
            if not isinstance(week, dict):
                continue
            days = week.get("days") or {}
            if not isinstance(days, dict):
                continue
            for _, day_payload in days.items():
                if not isinstance(day_payload, dict):
                    continue
                if str(day_payload.get("date") or "") == iso_target:
                    return _from_day_payload(day_payload)

        # fallback для by_weeks: если конкретная дата не заполнена, считаем выходным
        return DayScheduleModel(is_day_off=True)

