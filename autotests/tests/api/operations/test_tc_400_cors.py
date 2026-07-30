from __future__ import annotations

from collections.abc import Callable

import pytest
from playwright.sync_api import Playwright

from autotests.config import Settings


PROTECTED_PATH = "/v1/auth/me"
UNTRUSTED_ORIGIN = "https://untrusted.invalid"
RoleApiTokenProvider = Callable[[str], str]


def _assert_origin_not_allowed(
    headers: dict[str, str],
    *,
    checkpoint: str,
) -> None:
    assert "access-control-allow-origin" not in headers, (
        f"{checkpoint} неизвестный origin не должен получать "
        "Access-Control-Allow-Origin"
    )
    assert "access-control-allow-credentials" not in headers, (
        f"{checkpoint} неизвестный origin не должен получать "
        "Access-Control-Allow-Credentials"
    )


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
@pytest.mark.xfail(
    reason=(
        "BUG-028: staging отражает любой Origin и разрешает credentials "
        "для preflight и защищённого GET"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_400_cors_allows_admin_and_rejects_unknown_origin(
    playwright: Playwright,
    api_base_url: str,
    test_settings: Settings,
    role_api_token: RoleApiTokenProvider,
) -> None:
    """
    TC-400 — CORS разрешает staging-админку, но не произвольный сайт.

    Используется только защищённый GET. Изменяющий запрос публичной
    demo-формы остаётся ручной частью кейса, чтобы не создавать заявки.
    """
    allowed_origin = test_settings.web_base_url
    authorization = f"Bearer {role_api_token('operator')}"
    request_context = playwright.request.new_context(base_url=api_base_url)
    try:
        allowed_preflight = request_context.fetch(
            PROTECTED_PATH,
            method="OPTIONS",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        allowed_preflight_status = allowed_preflight.status
        allowed_preflight_headers = allowed_preflight.headers

        allowed_get = request_context.get(
            PROTECTED_PATH,
            headers={
                "Origin": allowed_origin,
                "Authorization": authorization,
            },
        )
        allowed_get_status = allowed_get.status
        allowed_get_headers = allowed_get.headers

        denied_preflight = request_context.fetch(
            PROTECTED_PATH,
            method="OPTIONS",
            headers={
                "Origin": UNTRUSTED_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        denied_preflight_headers = denied_preflight.headers

        denied_get = request_context.get(
            PROTECTED_PATH,
            headers={
                "Origin": UNTRUSTED_ORIGIN,
                "Authorization": authorization,
            },
        )
        denied_get_status = denied_get.status
        denied_get_headers = denied_get.headers
    finally:
        request_context.dispose()

    assert allowed_preflight_status == 204, (
        "[TC-400:allowed-preflight] ожидали HTTP 204, получили "
        f"{allowed_preflight_status}"
    )
    assert (
        allowed_preflight_headers.get("access-control-allow-origin")
        == allowed_origin
    ), (
        "[TC-400:allowed-preflight] ожидали точный разрешённый origin "
        f"{allowed_origin!r}, получили "
        f"{allowed_preflight_headers.get('access-control-allow-origin')!r}"
    )
    assert (
        allowed_preflight_headers.get("access-control-allow-credentials")
        == "true"
    ), (
        "[TC-400:allowed-preflight] credentialed admin-запрос должен быть "
        "разрешён"
    )
    assert "GET" in allowed_preflight_headers.get(
        "access-control-allow-methods",
        "",
    ), (
        "[TC-400:allowed-preflight] разрешённые методы должны содержать GET"
    )
    assert "authorization" in allowed_preflight_headers.get(
        "access-control-allow-headers",
        "",
    ).lower(), (
        "[TC-400:allowed-preflight] разрешённые заголовки должны содержать "
        "Authorization"
    )

    assert allowed_get_status == 200, (
        "[TC-400:allowed-get] защищённый GET с origin админки должен "
        f"вернуть 200, получено {allowed_get_status}"
    )
    assert (
        allowed_get_headers.get("access-control-allow-origin")
        == allowed_origin
    ), (
        "[TC-400:allowed-get] ответ должен разрешать только точный origin "
        "админки"
    )
    assert (
        allowed_get_headers.get("access-control-allow-credentials") == "true"
    ), (
        "[TC-400:allowed-get] ответ должен разрешать credentialed-запрос "
        "админки"
    )

    _assert_origin_not_allowed(
        denied_preflight_headers,
        checkpoint="[TC-400:denied-preflight]",
    )
    assert denied_get_status == 200, (
        "[TC-400:denied-get] серверная авторизация безопасного GET должна "
        f"остаться независимой от CORS, получено {denied_get_status}"
    )
    _assert_origin_not_allowed(
        denied_get_headers,
        checkpoint="[TC-400:denied-get]",
    )
