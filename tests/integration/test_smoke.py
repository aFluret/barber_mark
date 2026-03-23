"""
/**
 * @file: test_smoke.py
 * @description: Базовый smoke-тест структуры проекта
 * @dependencies: src.main
 * @created: 2026-03-23
 */
"""


def test_smoke_import_main() -> None:
    from src.main import build_dispatcher

    dispatcher = build_dispatcher()
    assert dispatcher is not None
