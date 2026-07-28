from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

import pytest
from playwright.sync_api import APIRequestContext, APIResponse, Playwright


RoleApiTokenProvider = Callable[[str], str]


def _authorization_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _response_snapshot(
    response: APIResponse,
) -> tuple[int, str, object]:
    status = response.status
    text = response.text()
    return status, text, response.json()


def _delete_created_rops(
    superadmin_context: APIRequestContext,
    *candidate_groups: object,
) -> None:
    user_ids: set[str] = set()
    for candidate_group in candidate_groups:
        candidates = (
            candidate_group
            if isinstance(candidate_group, list)
            else [candidate_group]
        )
        for item in candidates:
            if not isinstance(item, dict):
                continue
            user_id = item.get("id")
            if isinstance(user_id, str) and user_id:
                user_ids.add(user_id)

    for user_id in user_ids:
        delete_response = superadmin_context.delete(
            f"/v1/users/{user_id}",
        )
        delete_status, delete_text, delete_body = _response_snapshot(
            delete_response
        )
        assert delete_status == 200, (
            "[TC-041 teardown] при удалении ошибочно созданного РОП "
            f"ожидали 200, получили {delete_status}: {delete_text}"
        )
        assert isinstance(delete_body, dict), (
            "[TC-041 teardown] ожидали JSON-объект удаления, "
            f"получили {delete_body!r}"
        )
        assert delete_body.get("message") == "o'chirildi", (
            "[TC-041 teardown] ожидали message=\"o'chirildi\", "
            f"получили {delete_body!r}"
        )


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
def test_tc_041_operator_cannot_create_rop(
    playwright: Playwright,
    api_base_url: str,
    role_api_token: RoleApiTokenProvider,
) -> None:
    """
    TC-041 — оператор не может создать РОП через API.

    Ожидаемый результат: валидный POST /v1/rops с токеном оператора
    возвращает точный 403 Forbidden / «ruxsat yo'q»; super-admin не
    находит нового пользователя по уникальному username.
    """
    unique_id = uuid4().hex
    username = f"AT-{unique_id[:8]}"
    payload = {
        "username": username,
        "password": f"AT!{unique_id[:12]}",
        "first_name": "AT",
        "last_name": "TC-041",
        "phone": f"+99890{uuid4().int % 10_000_000:07d}",
        "company_name": f"AT-{uuid4().hex[:8]}",
        "tariff": "taxlil_dashboard",
    }
    operator_token = role_api_token("operator")
    superadmin_token = role_api_token("superadmin")
    operator_context = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers=_authorization_headers(operator_token),
    )
    superadmin_context = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers=_authorization_headers(superadmin_token),
    )
    listed_items: object = None
    create_body: object = None

    try:
        create_response = operator_context.post(
            "/v1/rops",
            data=payload,
        )
        create_status, create_text, create_body = _response_snapshot(
            create_response
        )
        list_response = superadmin_context.get(
            "/v1/users",
            params={
                "filter": f"username='{username}'",
                "page": 1,
                "perPage": 100,
            },
        )
        list_status, list_text, list_body = _response_snapshot(
            list_response
        )
        listed_items = (
            list_body.get("items")
            if isinstance(list_body, dict)
            else None
        )
    finally:
        _delete_created_rops(
            superadmin_context,
            create_body,
            listed_items,
        )
        operator_context.dispose()
        superadmin_context.dispose()

    assert create_status == 403, (
        "[TC-041] оператору ожидали 403 при создании РОП, "
        f"получили {create_status}: {create_text}"
    )
    expected_error = {
        "$schema": f"{api_base_url}/schemas/ErrorModel.json",
        "title": "Forbidden",
        "status": 403,
        "detail": "ruxsat yo'q",
    }
    assert create_body == expected_error, (
        f"[TC-041] ожидали точную ошибку {expected_error!r}, "
        f"получили {create_body!r}"
    )
    assert list_status == 200, (
        "[TC-041] при контрольном поиске РОП ожидали 200, "
        f"получили {list_status}: {list_text}"
    )
    assert isinstance(list_body, dict), (
        "[TC-041] при контрольном поиске ожидали JSON-объект, "
        f"получили {list_body!r}"
    )
    assert list_body.get("page") == 1, (
        f"[TC-041] ожидали page=1, получили {list_body!r}"
    )
    assert list_body.get("perPage") == 100, (
        f"[TC-041] ожидали perPage=100, получили {list_body!r}"
    )
    assert list_body.get("totalItems") == 0, (
        "[TC-041] оператор не должен создать РОП: ожидали totalItems=0, "
        f"получили {list_body!r}"
    )
    assert listed_items == [], (
        "[TC-041] оператор не должен создать РОП: ожидали items=[], "
        f"получили {listed_items!r}"
    )
