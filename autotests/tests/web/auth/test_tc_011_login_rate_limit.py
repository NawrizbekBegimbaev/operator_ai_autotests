from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
@pytest.mark.ratelimit
@pytest.mark.manual_setup
@pytest.mark.slow
@pytest.mark.serial
def test_tc_011_login_rate_limit_requires_dedicated_account() -> None:
    """
    TC-011 — защита входа от шести неверных попыток подряд.

    Ожидаемый результат: шестая попытка за минуту отклоняется сообщением
    о превышении лимита; после окончания минутного окна верный вход снова
    работает. Кейс запускается серийно только на выделенной учётной записи.
    """
    pytest.skip(
        "TC-011: не задана выделенная rate-limit учётная запись; "
        "сжигать лимит учёток основного прогона запрещено"
    )
