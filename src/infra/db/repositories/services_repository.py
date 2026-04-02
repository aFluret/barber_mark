"""
/**
 * @file: services_repository.py
 * @description: Репозиторий справочника услуг для Supabase.
 * @dependencies: infra.db.models, infra.db.supabase_client, asyncio
 * @created: 2026-04-02
 */
"""

from __future__ import annotations

import asyncio
from typing import List, Optional

from src.infra.db.models import ServiceModel
from src.infra.db.supabase_client import get_supabase_client


class ServicesRepository:
    async def list_all(self) -> List[ServiceModel]:
        def _op() -> List[ServiceModel]:
            client = get_supabase_client()
            res = (
                client.table("services")
                .select("id,name,price_byn,duration_minutes")
                .order("id")
                .execute()
            )
            out: List[ServiceModel] = []
            for row in res.data or []:
                out.append(
                    ServiceModel(
                        id=int(row["id"]),
                        name=str(row["name"]),
                        price_byn=int(row["price_byn"]),
                        duration_minutes=int(row["duration_minutes"]),
                    )
                )
            return out

        return await asyncio.to_thread(_op)

    async def get_by_id(self, service_id: int) -> Optional[ServiceModel]:
        def _op() -> Optional[ServiceModel]:
            client = get_supabase_client()
            res = (
                client.table("services")
                .select("id,name,price_byn,duration_minutes")
                .eq("id", service_id)
                .limit(1)
                .execute()
            )
            row = (res.data or [None])[0]
            if not row:
                return None
            return ServiceModel(
                id=int(row["id"]),
                name=str(row["name"]),
                price_byn=int(row["price_byn"]),
                duration_minutes=int(row["duration_minutes"]),
            )

        return await asyncio.to_thread(_op)

    async def upsert_service(self, service: ServiceModel) -> None:
        """
        Простая upsert-операция для админского редактирования справочника услуг.
        """

        def _op() -> None:
            client = get_supabase_client()
            payload = {
                "id": service.id,
                "name": service.name,
                "price_byn": service.price_byn,
                "duration_minutes": service.duration_minutes,
            }
            client.table("services").upsert(payload, on_conflict="id").execute()

        await asyncio.to_thread(_op)

