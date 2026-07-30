from __future__ import annotations

import re
from dataclasses import dataclass

import pytest
from playwright.sync_api import APIRequestContext, Playwright


@dataclass(frozen=True)
class ServiceResponse:
    status: int
    content_type: str
    text: str


SENSITIVE_PATTERNS = {
    "секрет в поле ответа": re.compile(
        r"(?i)\b(?:password|client_secret|access_token|refresh_token|"
        r"authorization|api[_-]?key)\b\s*(?:=|:)\s*[\"']?[^\s,\"'}]+"
    ),
    "Bearer-токен": re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{16,}"),
    "JWT": re.compile(
        r"\beyJ[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}"
        r"\.[a-zA-Z0-9_-]{8,}\b"
    ),
    "закрытый ключ": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "email клиента": re.compile(
        r"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@"
        r"[a-z0-9.-]+\.[a-z]{2,}(?![a-z0-9.-])"
    ),
    "телефон клиента": re.compile(r"(?<!\d)\+?998(?:[\s-]?\d){9}(?!\d)"),
    "UUID клиента": re.compile(
        r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
        r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b"
    ),
}


def _get(request_context: APIRequestContext, path: str) -> ServiceResponse:
    response = request_context.get(path)
    return ServiceResponse(
        status=response.status,
        content_type=response.headers.get("content-type", ""),
        text=response.text(),
    )


def _assert_no_sensitive_data(
    responses: dict[str, ServiceResponse],
) -> None:
    findings: list[str] = []
    for path, response in responses.items():
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(response.text):
                findings.append(f"{path}: {label}")

    assert not findings, (
        "[TC-373] служебные ответы содержат потенциально чувствительные "
        f"данные ({'; '.join(findings)}). Содержимое ответа намеренно не "
        "выводится в отчёт."
    )


def _assert_health_contract(
    response: ServiceResponse,
    *,
    path: str,
    expected_status_value: str,
) -> None:
    assert response.status == 200, (
        f"[TC-373:{path}] ожидали HTTP 200, получили {response.status}"
    )
    assert response.content_type.startswith("application/json"), (
        f"[TC-373:{path}] ожидали JSON, получили "
        f"Content-Type={response.content_type!r}"
    )
    assert response.text.strip() == (
        f'{{"status":"{expected_status_value}"}}'
    ), (
        f"[TC-373:{path}] ожидали единственное поле status со значением "
        f"{expected_status_value!r}; фактическое тело скрыто"
    )


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.security
def test_tc_373_service_health_readiness_and_metrics_are_safe(
    playwright: Playwright,
    api_base_url: str,
) -> None:
    """
    TC-373 — служебные endpoints подтверждают здоровье релиза.

    Проверка не создаёт телефонный звонок на staging: после первой серии
    выполняется безопасный публичный бизнес-запрос, затем health/readiness
    проверяются повторно. Постусловие после реального тестового звонка остаётся
    частью ручной эксплуатационной приёмки.
    """
    request_context = playwright.request.new_context(base_url=api_base_url)
    try:
        first_health = _get(request_context, "/healthz")
        first_readiness = _get(request_context, "/readyz")
        metrics = _get(request_context, "/metrics")

        business_response = request_context.get("/v1/plans")
        business_status = business_response.status

        second_health = _get(request_context, "/healthz")
        second_readiness = _get(request_context, "/readyz")
    finally:
        request_context.dispose()

    _assert_health_contract(
        first_health,
        path="/healthz:first",
        expected_status_value="ok",
    )
    _assert_health_contract(
        first_readiness,
        path="/readyz:first",
        expected_status_value="ready",
    )
    assert business_status == 200, (
        "[TC-373:/v1/plans] безопасный контрольный запрос должен вернуть "
        f"200, получено {business_status}"
    )
    _assert_health_contract(
        second_health,
        path="/healthz:after-business-request",
        expected_status_value="ok",
    )
    _assert_health_contract(
        second_readiness,
        path="/readyz:after-business-request",
        expected_status_value="ready",
    )

    assert metrics.status == 200, (
        f"[TC-373:/metrics] ожидали HTTP 200, получили {metrics.status}"
    )
    assert metrics.content_type.startswith("text/plain"), (
        "[TC-373:/metrics] ожидали Prometheus text format, получили "
        f"Content-Type={metrics.content_type!r}"
    )
    assert "# HELP " in metrics.text and "# TYPE " in metrics.text, (
        "[TC-373:/metrics] ответ не содержит обязательные HELP/TYPE "
        "декларации Prometheus"
    )
    assert "http_requests_total" in metrics.text, (
        "[TC-373:/metrics] отсутствует прикладная метрика "
        "http_requests_total"
    )

    _assert_no_sensitive_data(
        {
            "/healthz:first": first_health,
            "/readyz:first": first_readiness,
            "/metrics": metrics,
            "/healthz:after-business-request": second_health,
            "/readyz:after-business-request": second_readiness,
        }
    )
