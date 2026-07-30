from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from autotests.support.login_rate_guard import LoginRateGuard


def login(
    request_context: APIRequestContext,
    login_rate_guard: LoginRateGuard,
    *,
    username: str,
    password: str,
) -> APIResponse:
    """Выполняет один безопасно разнесённый по времени вход на staging."""
    login_rate_guard.before_attempt()
    return request_context.post(
        "/v1/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def require_json_object(
    response: APIResponse,
    *,
    checkpoint: str,
) -> dict[str, Any]:
    body = response.json()
    assert isinstance(body, dict), (
        f"{checkpoint} ожидали JSON-объект, получили {body!r}"
    )
    return body


def require_access_token(
    response: APIResponse,
    *,
    checkpoint: str,
) -> tuple[str, dict[str, Any]]:
    assert response.status == 200, (
        f"{checkpoint} ожидали HTTP 200, получили {response.status}: "
        f"{response.text()}"
    )
    body = require_json_object(response, checkpoint=checkpoint)
    access_token = body.get("access_token")
    assert isinstance(access_token, str) and access_token, (
        f"{checkpoint} ожидали непустой access_token, получили {body!r}"
    )
    user = body.get("user")
    assert isinstance(user, dict), (
        f"{checkpoint} ожидали объект user, получили {body!r}"
    )
    return access_token, user
