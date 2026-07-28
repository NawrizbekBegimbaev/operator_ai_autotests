from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.manual_setup
def test_tc_035_operator_cannot_open_foreign_call_by_direct_url() -> None:
    """
    TC-035 — оператор не открывает чужую карточку звонка по прямой ссылке.

    Ожидаемый результат: карточка звонка оператора РОП-Б возвращает
    «нет доступа» или «не найдено»; аудиозапись и точный текст разговора
    чужой компании недоступны оператору РОП-А.
    """
    pytest.skip(
        "TC-035: нужен реальный завершённый звонок оператора второго РОП "
        "с доступными записью и транскрипцией; такой звонок нельзя "
        "безопасно создать через API текущего стенда."
    )
