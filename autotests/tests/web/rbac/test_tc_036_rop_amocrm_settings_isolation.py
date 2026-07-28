from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.manual_setup
def test_tc_036_rop_sees_only_own_amocrm_settings() -> None:
    """
    TC-036 — РОП-А не видит настройки и воронку РОП-Б.

    Ожидаемый результат: «Правила», «Настройка очереди» и «Критерии»
    содержат только воронки, статусы и операторов РОП-А; названия
    воронок РОП-Б отсутствуют на всех трёх экранах.
    """
    pytest.skip(
        "TC-036: нужны две вручную подключённые тестовые AmoCRM с "
        "заранее известными разными воронками и статусами; текущий API "
        "не позволяет безопасно подготовить эти внешние данные."
    )
