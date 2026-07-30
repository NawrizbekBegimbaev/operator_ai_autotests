from __future__ import annotations

import pytest
from playwright.sync_api import APIRequestContext

from autotests.support.auth_requests import require_json_object
from autotests.support.operator_api import (
    cleanup_users_by_username,
    list_operators,
    list_users_by_username,
)
from autotests.support.temporary_users import OperatorDraft


def _delete_new_users(
    rop_request: APIRequestContext,
    *,
    username: str,
    preserved_ids: set[str],
    checkpoint: str,
) -> None:
    users = list_users_by_username(
        rop_request,
        username,
        checkpoint=checkpoint,
    )
    for user in users:
        user_id = user.get("id")
        if isinstance(user_id, str) and user_id not in preserved_ids:
            response = rop_request.delete(f"/v1/users/{user_id}")
            assert response.status == 200, (
                f"{checkpoint} при удалении неожиданного дубликата ожидали "
                f"200, получили {response.status}: {response.text()}"
            )


@pytest.mark.api
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.validation
def test_tc_057_operator_phone_must_be_unique_across_formatting(
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-057 — форматирование номера не обходит проверку уникальности."""
    operators = list_operators(
        rop_api_request,
        checkpoint="[TC-057 setup]",
    )
    existing = next(
        (
            operator
            for operator in operators
            if isinstance(operator.get("phone"), str)
            and any(character.isdigit() for character in operator["phone"])
        ),
        None,
    )
    assert existing is not None, (
        "[TC-057 setup] нужен существующий оператор с телефоном"
    )
    existing_phone = existing["phone"]
    same_digits_without_formatting = "".join(
        character for character in existing_phone if character.isdigit()
    )
    payload = operator_draft.api_payload()
    payload["phone"] = same_digits_without_formatting

    try:
        response = rop_api_request.post("/v1/operators", data=payload)
        assert response.status == 400, (
            "[TC-057] повторный телефон должен вернуть 400, получили "
            f"{response.status}: {response.text()}"
        )
        body = require_json_object(
            response,
            checkpoint="[TC-057] ответ уникальности телефона",
        )
        assert (
            body.get("detail")
            == "validatsiya xatosi: phone: Bu telefon raqami allaqachon band"
        ), (
            "[TC-057] ожидали понятную ошибку занятого телефона, "
            f"получили {body!r}"
        )
        created = list_users_by_username(
            rop_api_request,
            operator_draft.username,
            checkpoint="[TC-057] проверка отсутствия оператора",
        )
        assert created == [], (
            "[TC-057] оператор с повторным телефоном не должен создаваться: "
            f"{created!r}"
        )
    finally:
        cleanup_users_by_username(
            rop_api_request,
            operator_draft.username,
            checkpoint="[TC-057 cleanup]",
        )


@pytest.mark.api
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.validation
def test_tc_058_operator_username_must_be_unique(
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-058 — занятый username не создаёт второго пользователя."""
    operators = list_operators(
        rop_api_request,
        checkpoint="[TC-058 setup]",
    )
    existing = next(
        (
            operator
            for operator in operators
            if isinstance(operator.get("username"), str)
            and operator["username"]
        ),
        None,
    )
    assert existing is not None, (
        "[TC-058 setup] нужен существующий оператор с username"
    )
    duplicate_username = existing["username"]
    before = list_users_by_username(
        rop_api_request,
        duplicate_username,
        checkpoint="[TC-058 setup] исходный пользователь",
    )
    preserved_ids = {
        user_id
        for user in before
        if isinstance((user_id := user.get("id")), str)
    }
    assert preserved_ids, (
        f"[TC-058 setup] у исходного пользователя нет id: {before!r}"
    )
    payload = operator_draft.api_payload()
    payload["username"] = duplicate_username

    try:
        response = rop_api_request.post("/v1/operators", data=payload)
        assert response.status == 409, (
            "[TC-058] занятый username должен вернуть 409, получили "
            f"{response.status}: {response.text()}"
        )
        body = require_json_object(
            response,
            checkpoint="[TC-058] ответ уникальности username",
        )
        assert body.get("detail") == "username allaqachon mavjud", (
            "[TC-058] ожидали понятную ошибку занятого username, "
            f"получили {body!r}"
        )

        after = list_users_by_username(
            rop_api_request,
            duplicate_username,
            checkpoint="[TC-058] проверка отсутствия дубликата",
        )
        after_ids = {
            user_id
            for user in after
            if isinstance((user_id := user.get("id")), str)
        }
        assert after_ids == preserved_ids, (
            "[TC-058] набор пользователей с занятым username изменился: "
            f"до={before!r}, после={after!r}"
        )
    finally:
        _delete_new_users(
            rop_api_request,
            username=duplicate_username,
            preserved_ids=preserved_ids,
            checkpoint="[TC-058 cleanup]",
        )
