from __future__ import annotations

from uuid import uuid4

import pytest
from playwright.sync_api import Playwright

from autotests.support.auth_requests import (
    login,
    require_access_token,
    require_json_object,
)
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.temporary_users import TemporaryOperator


@pytest.mark.api
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.auth
@pytest.mark.serial
def test_tc_018_rop_resets_operator_password(
    playwright: Playwright,
    api_base_url: str,
    login_rate_guard: LoginRateGuard,
    temporary_operator: TemporaryOperator,
) -> None:
    """TC-018 — РОП задаёт оператору новый пароль, старый больше не работает."""
    public_request = playwright.request.new_context(base_url=api_base_url)
    new_password = f"Reset!{uuid4().hex[:12]}"
    try:
        reset_response = temporary_operator.rop_request.post(
            f"/v1/users/{temporary_operator.id}/password",
            data={"new_password": new_password},
        )
        assert reset_response.status == 200, (
            "[TC-018] при сбросе пароля ожидали 200, получили "
            f"{reset_response.status}: {reset_response.text()}"
        )
        reset_body = require_json_object(
            reset_response,
            checkpoint="[TC-018] сброс пароля",
        )
        assert reset_body.get("message") == "parol yangilandi", (
            "[TC-018] ожидали message='parol yangilandi', "
            f"получили {reset_body!r}"
        )

        old_password_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        assert old_password_login.status == 401, (
            "[TC-018] старый пароль должен перестать работать: ожидали 401, "
            f"получили {old_password_login.status}: "
            f"{old_password_login.text()}"
        )

        new_password_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=new_password,
        )
        _, reset_user = require_access_token(
            new_password_login,
            checkpoint="[TC-018] вход с новым паролем",
        )
        assert reset_user.get("id") == temporary_operator.id, (
            "[TC-018] с новым паролем вошёл другой оператор: "
            f"{reset_user!r}"
        )
    finally:
        public_request.dispose()
