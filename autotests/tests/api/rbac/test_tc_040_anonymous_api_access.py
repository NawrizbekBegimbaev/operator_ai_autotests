from __future__ import annotations

import pytest
from playwright.sync_api import Playwright


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
def test_tc_040_users_request_without_token_is_rejected(
    playwright: Playwright,
    api_base_url: str,
) -> None:
    """
    TC-040 — API-запрос списка пользователей без токена отклоняется.

    Ожидаемый результат: GET /v1/users без Authorization возвращает
    HTTP 401 и только точную локализованную ошибку; данные пользователей
    в теле отсутствуют.
    """
    request_context = playwright.request.new_context(
        base_url=api_base_url,
    )
    try:
        response = request_context.get("/v1/users")
        actual_status = response.status
        actual_content_type = response.headers.get("content-type")
        response_text = response.text()
        body = response.json()
    finally:
        request_context.dispose()

    assert actual_status == 401, (
        f"[TC-040] ожидали 401 без токена, получили "
        f"{actual_status}: {response_text}"
    )
    assert actual_content_type == "text/plain; charset=utf-8", (
        "[TC-040] ожидали Content-Type 'text/plain; charset=utf-8', "
        f"получили {actual_content_type!r}: {response_text}"
    )
    expected_body = {
        "title": "Avtorizatsiya xatosi",
        "status": 401,
        "detail": "Authorization sarlavhasi topilmadi",
    }
    assert body == expected_body, (
        f"[TC-040] ожидали только точную ошибку {expected_body!r}, "
        f"получили {body!r}"
    )
