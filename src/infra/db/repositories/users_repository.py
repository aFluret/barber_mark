"""
/**
 * @file: users_repository.py
 * @description: Репозиторий пользователей для Supabase
 * @dependencies: infra.db.models, infra.db.supabase_client, asyncio
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

import asyncio
from typing import Optional

from src.infra.db.models import UserModel
from src.infra.db.supabase_client import get_supabase_client
from datetime import datetime


class UsersRepository:
    async def get_by_user_id(self, user_id: int) -> Optional[UserModel]:
        def _op() -> Optional[dict]:
            client = get_supabase_client()
            res = (
                client.table("users")
                .select("user_id, phone, name, created_at")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            return res.data[0] if res.data else None

        row = await asyncio.to_thread(_op)
        if not row:
            return None

        created_at = row.get("created_at")
        if isinstance(created_at, str):
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            created_at_dt = created_at

        return UserModel(
            user_id=int(row["user_id"]),
            phone=str(row["phone"]),
            name=str(row["name"]),
            created_at=created_at_dt,
        )

    async def upsert(self, user: UserModel) -> None:
        def _op() -> None:
            client = get_supabase_client()
            payload = {
                "user_id": user.user_id,
                "phone": user.phone,
                "name": user.name,
            }
            client.table("users").upsert(payload, on_conflict="user_id").execute()

        await asyncio.to_thread(_op)
