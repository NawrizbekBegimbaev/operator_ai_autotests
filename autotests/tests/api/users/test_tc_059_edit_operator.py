from __future__ import annotations

from uuid import uuid4

import pytest
from playwright.sync_api import APIRequestContext

from autotests.support.auth_requests import require_json_object
from autotests.support.temporary_users import TemporaryOperator


@pytest.mark.api
@pytest.mark.high
@pytest.mark.positive
def test_tc_059_rop_edits_own_operator_and_preserves_scope(
    temporary_operator: TemporaryOperator,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-059 — данные меняются, роль и компания оператора сохраняются."""
    before_response = rop_api_request.get(
        f"/v1/users/{temporary_operator.id}"
    )
    assert before_response.status == 200, (
        "[TC-059 setup] перед изменением ожидали GET 200, получили "
        f"{before_response.status}: {before_response.text()}"
    )
    before = require_json_object(
        before_response,
        checkpoint="[TC-059 setup]",
    )

    unique_id = uuid4().hex
    updated_fields = {
        "first_name": f"Edited{unique_id[:5]}",
        "last_name": f"Operator{unique_id[5:10]}",
        "username": f"AT-EDIT-{unique_id[:8]}",
        "phone": f"+99891{uuid4().int % 10_000_000:07d}",
        "pbx_extension": f"AT{unique_id[:6]}",
        "salary": 2_000_000,
        "salary_day": temporary_operator.salary_day,
    }

    patch_response = rop_api_request.patch(
        f"/v1/users/{temporary_operator.id}",
        data=updated_fields,
    )
    assert patch_response.status == 200, (
        "[TC-059] при изменении оператора ожидали 200, получили "
        f"{patch_response.status}: {patch_response.text()}"
    )
    patched = require_json_object(
        patch_response,
        checkpoint="[TC-059] PATCH оператора",
    )

    refresh_response = rop_api_request.get(
        f"/v1/users/{temporary_operator.id}"
    )
    assert refresh_response.status == 200, (
        "[TC-059] после обновления ожидали GET 200, получили "
        f"{refresh_response.status}: {refresh_response.text()}"
    )
    refreshed = require_json_object(
        refresh_response,
        checkpoint="[TC-059] GET после обновления",
    )

    for field, expected in updated_fields.items():
        assert patched.get(field) == expected, (
            f"[TC-059] PATCH вернул неверное поле {field!r}: "
            f"ожидали {expected!r}, получили {patched.get(field)!r}"
        )
        assert refreshed.get(field) == expected, (
            f"[TC-059] после повторного GET поле {field!r} не сохранилось: "
            f"ожидали {expected!r}, получили {refreshed.get(field)!r}"
        )

    assert refreshed.get("role") == before.get("role") == "operator", (
        "[TC-059] роль оператора изменилась: "
        f"до={before.get('role')!r}, после={refreshed.get('role')!r}"
    )
    assert refreshed.get("company_id") == before.get("company_id"), (
        "[TC-059] компания оператора изменилась: "
        f"до={before.get('company_id')!r}, "
        f"после={refreshed.get('company_id')!r}"
    )
    assert refreshed.get("id") == temporary_operator.id, (
        "[TC-059] вместо обновления создан другой пользователь: "
        f"{refreshed!r}"
    )
