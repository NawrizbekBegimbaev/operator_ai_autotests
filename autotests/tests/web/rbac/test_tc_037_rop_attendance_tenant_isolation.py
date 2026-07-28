from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.manual_setup
def test_tc_037_rop_sees_only_own_operator_attendance() -> None:
    """
    TC-037 — РОП-А не видит посещаемость операторов РОП-Б.

    Ожидаемый результат: за текущую неделю в «Посещаемости» показаны
    только операторы РОП-А; операторы и смены РОП-Б отсутствуют.
    """
    pytest.skip(
        "TC-037: у операторов второго РОП нужны реальные смены и "
        "перерывы за текущую неделю; стенд не предоставляет API для "
        "безопасной подготовки таких данных."
    )
