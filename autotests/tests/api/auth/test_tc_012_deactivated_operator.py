from __future__ import annotations

import pytest
from playwright.sync_api import Playwright

from autotests.support.auth_requests import (
    login,
    require_access_token,
    require_json_object,
)
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.temporary_users import TemporaryOperator


PRESERVED_FIELDS = (
    "username",
    "role",
    "first_name",
    "last_name",
    "phone",
    "company_id",
    "pbx_extension",
    "salary",
    "salary_day",
)


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.serial
def test_tc_012_deactivation_blocks_login_and_preserves_operator_data(
    playwright: Playwright,
    api_base_url: str,
    login_rate_guard: LoginRateGuard,
    temporary_operator: TemporaryOperator,
) -> None:
    """
    TC-012 — деактивированный оператор не входит и не теряет свои данные.

    API-часть дополнительно проверяет, что уже выданный access token
    отклоняется на следующем запросе, а повторная активация возвращает вход.
    """
    public_request = playwright.request.new_context(base_url=api_base_url)
    try:
        before_response = temporary_operator.rop_request.get(
            f"/v1/users/{temporary_operator.id}"
        )
        assert before_response.status == 200, (
            "[TC-012 setup] перед деактивацией ожидали GET оператора 200, "
            f"получили {before_response.status}: {before_response.text()}"
        )
        before = require_json_object(
            before_response,
            checkpoint="[TC-012 setup]",
        )
        assert before.get("is_active") is True, (
            "[TC-012 setup] тестовый оператор должен быть активен: "
            f"{before!r}"
        )

        active_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        active_token, active_user = require_access_token(
            active_login,
            checkpoint="[TC-012 setup] вход активного оператора",
        )
        assert active_user.get("id") == temporary_operator.id, (
            "[TC-012 setup] вошёл другой оператор: "
            f"ожидали id={temporary_operator.id!r}, получили {active_user!r}"
        )

        deactivate_response = temporary_operator.rop_request.patch(
            f"/v1/users/{temporary_operator.id}",
            data={"is_active": False},
        )
        assert deactivate_response.status == 200, (
            "[TC-012] при деактивации ожидали HTTP 200, получили "
            f"{deactivate_response.status}: {deactivate_response.text()}"
        )
        deactivated = require_json_object(
            deactivate_response,
            checkpoint="[TC-012] деактивация",
        )
        assert deactivated.get("is_active") is False, (
            "[TC-012] после PATCH ожидали is_active=false, "
            f"получили {deactivated!r}"
        )

        blocked_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        assert blocked_login.status == 403, (
            "[TC-012] вход деактивированного оператора должен вернуть 403, "
            f"получили {blocked_login.status}: {blocked_login.text()}"
        )
        blocked_body = require_json_object(
            blocked_login,
            checkpoint="[TC-012] вход после деактивации",
        )
        assert blocked_body.get("detail") == "hisob faolsizlantirilgan", (
            "[TC-012] ожидали сообщение деактивированной учётной записи, "
            f"получили {blocked_body!r}"
        )

        live_token_response = public_request.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {active_token}"},
        )
        assert live_token_response.status == 401, (
            "[TC-012] старый access token должен быть отклонён сразу: "
            f"ожидали 401, получили {live_token_response.status}: "
            f"{live_token_response.text()}"
        )
        live_token_body = require_json_object(
            live_token_response,
            checkpoint="[TC-012] запрос со старым access token",
        )
        assert live_token_body.get("detail") == "Hisob faol emas", (
            "[TC-012] ожидали точную причину отказа для старого токена, "
            f"получили {live_token_body!r}"
        )

        after_response = temporary_operator.rop_request.get(
            f"/v1/users/{temporary_operator.id}"
        )
        assert after_response.status == 200, (
            "[TC-012] после деактивации данные оператора должны читаться РОП: "
            f"получили {after_response.status}: {after_response.text()}"
        )
        after = require_json_object(
            after_response,
            checkpoint="[TC-012] данные после деактивации",
        )
        for field in PRESERVED_FIELDS:
            assert after.get(field) == before.get(field), (
                f"[TC-012] поле {field!r} изменилось при деактивации: "
                f"до={before.get(field)!r}, после={after.get(field)!r}"
            )

        reactivate_response = temporary_operator.rop_request.patch(
            f"/v1/users/{temporary_operator.id}",
            data={"is_active": True},
        )
        assert reactivate_response.status == 200, (
            "[TC-012 teardown-check] при повторной активации ожидали 200, "
            f"получили {reactivate_response.status}: "
            f"{reactivate_response.text()}"
        )
        reactivated = require_json_object(
            reactivate_response,
            checkpoint="[TC-012] повторная активация",
        )
        assert reactivated.get("is_active") is True, (
            "[TC-012] после повторной активации ожидали is_active=true, "
            f"получили {reactivated!r}"
        )

        restored_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        _, restored_user = require_access_token(
            restored_login,
            checkpoint="[TC-012] вход после повторной активации",
        )
        assert restored_user.get("id") == temporary_operator.id, (
            "[TC-012] после активации вошёл другой оператор: "
            f"{restored_user!r}"
        )
    finally:
        public_request.dispose()
