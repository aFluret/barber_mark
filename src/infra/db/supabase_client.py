"""
/**
 * @file: supabase_client.py
 * @description: Lazy-провайдер клиента Supabase для репозиториев
 * @dependencies: infra.config.settings, supabase
 * @created: 2026-03-23
 */
"""

from __future__ import annotations

from typing import Optional

from supabase import Client, create_client

from src.infra.config.settings import get_settings

_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Создает клиент Supabase лениво, чтобы модуль можно было импортировать
    даже без настроенных env-переменных (для тестов/сборки).
    """

    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "Supabase не настроен. Укажите SUPABASE_URL и SUPABASE_SERVICE_ROLE_KEY в .env"
        )

    _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client

