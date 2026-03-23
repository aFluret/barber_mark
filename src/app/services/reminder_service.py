"""
/**
 * @file: reminder_service.py
 * @description: Заготовка сервиса напоминаний
 * @dependencies: infra.scheduler.jobs
 * @created: 2026-03-23
 */
"""


class ReminderService:
    def schedule_reminders(self, appointment_id: int) -> None:
        # TODO: подключить APScheduler и реальную отправку уведомлений.
        _ = appointment_id
