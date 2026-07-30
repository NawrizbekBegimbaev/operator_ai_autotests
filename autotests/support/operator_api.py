from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext


class OperatorApiContractError(RuntimeError):
    """API управления операторами вернул неожиданный контракт."""


def _require_items(
    response_status: int,
    response_text: str,
    response_body: Any,
    *,
    checkpoint: str,
    resource_name: str,
) -> list[dict[str, Any]]:
    if response_status != 200:
        raise OperatorApiContractError(
            f"{checkpoint} при чтении {resource_name} ожидали 200, "
            f"получили {response_status}: {response_text}"
        )
    if not isinstance(response_body, dict):
        raise OperatorApiContractError(
            f"{checkpoint} ожидали JSON-объект {resource_name}, "
            f"получили {response_body!r}"
        )
    items = response_body.get("items")
    if not isinstance(items, list):
        raise OperatorApiContractError(
            f"{checkpoint} ожидали массив items, получили {response_body!r}"
        )
    if not all(isinstance(item, dict) for item in items):
        raise OperatorApiContractError(
            f"{checkpoint} список содержит не-объект: {items!r}"
        )
    return items


def list_users_by_username(
    rop_request: APIRequestContext,
    username: str,
    *,
    checkpoint: str,
) -> list[dict[str, Any]]:
    if "'" in username:
        raise ValueError("Тестовый username не должен содержать апостроф.")
    response = rop_request.get(
        "/v1/users",
        params={
            "filter": f"username='{username}'",
            "page": 1,
            "perPage": 100,
        },
    )
    assert response.status == 200, (
        f"{checkpoint} при поиске пользователя ожидали 200, "
        f"получили {response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"{checkpoint} ожидали JSON-объект списка, получили {body!r}"
    )
    items = body.get("items")
    assert isinstance(items, list), (
        f"{checkpoint} ожидали массив items, получили {body!r}"
    )
    assert all(isinstance(item, dict) for item in items), (
        f"{checkpoint} список содержит не-объект: {items!r}"
    )
    return items


def list_operators(
    rop_request: APIRequestContext,
    *,
    checkpoint: str,
) -> list[dict[str, Any]]:
    response = rop_request.get(
        "/v1/users",
        params={
            "filter": "role='operator'",
            "page": 1,
            "perPage": 100,
        },
    )
    return _require_items(
        response.status,
        response.text(),
        response.json(),
        checkpoint=checkpoint,
        resource_name="операторов",
    )


def list_extensions(
    rop_request: APIRequestContext,
    *,
    checkpoint: str,
) -> list[dict[str, Any]]:
    response = rop_request.get("/v1/onlinepbx/extensions")
    return _require_items(
        response.status,
        response.text(),
        response.json(),
        checkpoint=checkpoint,
        resource_name="PBX extension",
    )


def list_operator_pipelines(
    rop_request: APIRequestContext,
    operator_id: str,
    *,
    checkpoint: str,
) -> list[dict[str, Any]]:
    response = rop_request.get(
        "/v1/operator-pipelines",
        params={"operator_id": operator_id},
    )
    return _require_items(
        response.status,
        response.text(),
        response.json(),
        checkpoint=checkpoint,
        resource_name="назначений воронок оператора",
    )


def get_operator(
    rop_request: APIRequestContext,
    operator_id: str,
    *,
    checkpoint: str,
) -> dict[str, Any]:
    response = rop_request.get(f"/v1/users/{operator_id}")
    if response.status != 200:
        raise OperatorApiContractError(
            f"{checkpoint} ожидали HTTP 200, получили "
            f"{response.status}: {response.text()}"
        )
    body = response.json()
    if not isinstance(body, dict):
        raise OperatorApiContractError(
            f"{checkpoint} ожидали JSON-объект оператора, получили {body!r}"
        )
    if body.get("id") != operator_id or body.get("role") != "operator":
        raise OperatorApiContractError(
            f"{checkpoint} API вернул другого пользователя: {body!r}"
        )
    return body


def cleanup_users_by_username(
    rop_request: APIRequestContext,
    username: str,
    *,
    checkpoint: str,
) -> None:
    users = list_users_by_username(
        rop_request,
        username,
        checkpoint=checkpoint,
    )
    for user in users:
        user_id = user.get("id")
        assert isinstance(user_id, str) and user_id, (
            f"{checkpoint} у найденного пользователя нет id: {user!r}"
        )
        response = rop_request.delete(f"/v1/users/{user_id}")
        assert response.status == 200, (
            f"{checkpoint} при удалении пользователя ожидали 200, "
            f"получили {response.status}: {response.text()}"
        )
