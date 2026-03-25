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
from datetime import datetime, time
from typing import List, Optional, Set

from src.infra.db.supabase_client import get_supabase_client


@dataclass(frozen=True)
class WorkScheduleModel:
    weekdays: Set[int]  # python weekday: Пн=0 ... Вс=6
    start_time: time
    end_time: time


class WorkScheduleRepository:
    async def get_latest(self) -> Optional[WorkScheduleModel]:
        def _op() -> Optional[dict]:
            client = get_supabase_client()
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

        # Supabase time может приходить как строка "HH:MM:SS" или "HH:MM".
        start_s = str(start_time_raw)[:5]
        end_s = str(end_time_raw)[:5]
        start_t = datetime.strptime(start_s, "%H:%M").time()
        end_t = datetime.strptime(end_s, "%H:%M").time()

        return WorkScheduleModel(
            weekdays=weekdays,
            start_time=start_t,
            end_time=end_t,
        )

    async def set_schedule(self, weekdays: List[int], start_time: time, end_time: time) -> None:
        payload = {
            "weekdays": list(weekdays),
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
        }

        def _op() -> None:
            client = get_supabase_client()
            # Для MVP оставляем одну актуальную запись: чистим и вставляем новую.
            client.table("work_schedule").delete().execute()
            client.table("work_schedule").insert(payload).execute()

        await asyncio.to_thread(_op)

