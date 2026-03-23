"""
/**
 * @file: test_schedule_service.py
 * @description: Unit-тест генерации временных слотов
 * @dependencies: app.services.schedule_service, pytest
 * @created: 2026-03-23
 */
"""

from src.app.services.schedule_service import ScheduleService


def test_generate_slots_half_hour_step() -> None:
    service = ScheduleService()
    slots = service.generate_slots("10:00", "11:30", 30)
    assert slots == ["10:00", "10:30", "11:00"]
