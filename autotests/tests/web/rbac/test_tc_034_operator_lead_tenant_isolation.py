from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.manual_setup
def test_tc_034_operator_sees_only_own_rop_funnel_leads() -> None:
    """
    TC-034 — оператор видит только лиды воронок своего РОП.

    Ожидаемый результат: в таблице «Звонки» отсутствуют лиды РОП-Б;
    оператор РОП-А видит только лиды назначенных ему воронок своего РОП.
    """
    pytest.skip(
        "TC-034: нужны две вручную настроенные тестовые AmoCRM с "
        "разными воронками и известными лидами; API-подготовки этих "
        "внешних данных на стенде сейчас нет."
    )
