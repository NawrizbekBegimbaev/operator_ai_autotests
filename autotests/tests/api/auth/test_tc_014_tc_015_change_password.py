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
def test_tc_014_operator_changes_own_password(
    playwright: Playwright,
    api_base_url: str,
    login_rate_guard: LoginRateGuard,
    temporary_operator: TemporaryOperator,
) -> None:
    """TC-014 — старый пароль перестаёт работать, новый позволяет войти."""
    public_request = playwright.request.new_context(base_url=api_base_url)
    new_password = f"New!{uuid4().hex[:12]}"
    try:
        initial_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        access_token, initial_user = require_access_token(
            initial_login,
            checkpoint="[TC-014] первоначальный вход",
        )
        assert initial_user.get("id") == temporary_operator.id, (
            "[TC-014] первоначально вошёл другой оператор: "
            f"{initial_user!r}"
        )

        change_response = public_request.post(
            "/v1/auth/change-password",
            data={
                "old_password": temporary_operator.password,
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert change_response.status == 200, (
            "[TC-014] при смене пароля ожидали 200, получили "
            f"{change_response.status}: {change_response.text()}"
        )
        change_body = require_json_object(
            change_response,
            checkpoint="[TC-014] смена пароля",
        )
        assert change_body.get("message") == "parol yangilandi", (
            "[TC-014] ожидали message='parol yangilandi', "
            f"получили {change_body!r}"
        )

        old_password_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        assert old_password_login.status == 401, (
            "[TC-014] старый пароль должен перестать работать: ожидали 401, "
            f"получили {old_password_login.status}: "
            f"{old_password_login.text()}"
        )

        new_password_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=new_password,
        )
        _, changed_user = require_access_token(
            new_password_login,
            checkpoint="[TC-014] вход с новым паролем",
        )
        assert changed_user.get("id") == temporary_operator.id, (
            "[TC-014] с новым паролем вошёл другой оператор: "
            f"{changed_user!r}"
        )
    finally:
        public_request.dispose()


@pytest.mark.api
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.serial
def test_tc_015_wrong_old_password_does_not_change_current_password(
    playwright: Playwright,
    api_base_url: str,
    login_rate_guard: LoginRateGuard,
    temporary_operator: TemporaryOperator,
) -> None:
    """TC-015 — неверный старый пароль отклоняется на сервере."""
    public_request = playwright.request.new_context(base_url=api_base_url)
    rejected_new_password = f"Rejected!{uuid4().hex[:10]}"
    try:
        initial_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        access_token, _ = require_access_token(
            initial_login,
            checkpoint="[TC-015] первоначальный вход",
        )

        change_response = public_request.post(
            "/v1/auth/change-password",
            data={
                "old_password": f"Wrong!{uuid4().hex[:10]}",
                "new_password": rejected_new_password,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert change_response.status == 400, (
            "[TC-015] неверный старый пароль должен вернуть 400, получили "
            f"{change_response.status}: {change_response.text()}"
        )
        change_body = require_json_object(
            change_response,
            checkpoint="[TC-015] отклонённая смена пароля",
        )
        assert change_body.get("detail") == "eski parol noto'g'ri", (
            "[TC-015] ожидали понятную причину отказа, "
            f"получили {change_body!r}"
        )

        current_password_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        _, current_user = require_access_token(
            current_password_login,
            checkpoint="[TC-015] повторный вход с текущим паролем",
        )
        assert current_user.get("id") == temporary_operator.id, (
            "[TC-015] после отказа вошёл другой оператор: "
            f"{current_user!r}"
        )
    finally:
        public_request.dispose()
