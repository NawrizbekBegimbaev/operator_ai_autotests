from __future__ import annotations

import pytest
from playwright.sync_api import Playwright


EXPECTED_PLAN_CODES = [
    "taxlil_dashboard",
    "taxlil_dashboard_auto_call",
    "full_ai",
]
EXPECTED_PLAN_FIELDS = {
    "code",
    "name",
    "price",
    "description",
    "features",
    "is_active",
    "sort",
}


@pytest.mark.api
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.security
def test_tc_228_public_api_returns_three_safe_plans(
    playwright: Playwright,
    api_base_url: str,
) -> None:
    """
    TC-228 — публичный API отдаёт три тарифа без авторизации.

    Ожидаемый результат: GET /v1/plans без токена возвращает 200 и
    ровно три тарифа с допустимыми уникальными кодами; каждый объект
    содержит только публичные поля, цена неотрицательна, features —
    массив строк, а элементы упорядочены по sort.
    """
    request_context = playwright.request.new_context(
        base_url=api_base_url,
    )
    try:
        response = request_context.get("/v1/plans")
        actual_status = response.status
        actual_headers = response.headers
        response_text = response.text()
        body = response.json()
    finally:
        request_context.dispose()

    assert actual_status == 200, (
        f"[TC-228] ожидали 200 без токена, получили "
        f"{actual_status}: {response_text}"
    )
    assert actual_headers.get("content-type") == "application/json", (
        "[TC-228] ожидали Content-Type 'application/json', "
        f"получили {actual_headers.get('content-type')!r}: {response_text}"
    )
    assert (
        actual_headers.get("link")
        == '</schemas/ListPlansOutputBody.json>; rel="describedBy"'
    ), (
        "[TC-228] ожидали ссылку на схему ListPlansOutputBody, "
        f"получили {actual_headers.get('link')!r}"
    )
    assert isinstance(body, dict), (
        f"[TC-228] ожидали JSON-объект, получили {body!r}"
    )
    assert set(body) == {"$schema", "items"}, (
        "[TC-228] публичный ответ должен содержать только $schema и "
        f"items, получили поля {set(body)!r}: {body!r}"
    )
    expected_schema = (
        f"{api_base_url}/schemas/ListPlansOutputBody.json"
    )
    assert body["$schema"] == expected_schema, (
        f"[TC-228] ожидали $schema={expected_schema!r}, "
        f"получили {body['$schema']!r}"
    )

    items = body["items"]
    assert isinstance(items, list), (
        f"[TC-228] ожидали массив items, получили {items!r}"
    )
    assert len(items) == 3, (
        f"[TC-228] ожидали ровно 3 тарифа, получили "
        f"{len(items)}: {items!r}"
    )
    assert all(isinstance(item, dict) for item in items), (
        f"[TC-228] каждый тариф должен быть JSON-объектом: {items!r}"
    )

    actual_codes = [item.get("code") for item in items]
    assert actual_codes == EXPECTED_PLAN_CODES, (
        f"[TC-228] ожидали коды по порядку {EXPECTED_PLAN_CODES!r}, "
        f"получили {actual_codes!r}"
    )
    actual_sorts = [item.get("sort") for item in items]
    assert all(
        isinstance(sort, int) and not isinstance(sort, bool)
        for sort in actual_sorts
    ), (
        f"[TC-228] каждый sort должен быть целым числом, получили "
        f"{actual_sorts!r}: {items!r}"
    )
    assert actual_sorts == sorted(actual_sorts), (
        f"[TC-228] ожидали порядок элементов по возрастанию sort, "
        f"получили {actual_sorts!r}: {items!r}"
    )

    for plan in items:
        code = plan["code"]
        assert set(plan) == EXPECTED_PLAN_FIELDS, (
            f"[TC-228:{code}] ожидали только публичные поля "
            f"{EXPECTED_PLAN_FIELDS!r}, получили {set(plan)!r}: {plan!r}"
        )
        assert isinstance(plan["name"], str) and plan["name"], (
            f"[TC-228:{code}] name должен быть непустой строкой: "
            f"{plan!r}"
        )
        assert isinstance(plan["price"], int) and not isinstance(
            plan["price"],
            bool,
        ), (
            f"[TC-228:{code}] price должен быть целым числом: {plan!r}"
        )
        assert plan["price"] >= 0, (
            f"[TC-228:{code}] price должен быть неотрицательным: "
            f"{plan!r}"
        )
        assert (
            isinstance(plan["description"], str)
            and plan["description"]
        ), (
            f"[TC-228:{code}] description должна быть непустой строкой: "
            f"{plan!r}"
        )
        assert isinstance(plan["features"], list), (
            f"[TC-228:{code}] features должен быть массивом: {plan!r}"
        )
        assert plan["features"], (
            f"[TC-228:{code}] features не должен быть пустым: {plan!r}"
        )
        assert all(
            isinstance(feature, str) and feature
            for feature in plan["features"]
        ), (
            f"[TC-228:{code}] каждая feature должна быть непустой "
            f"строкой: {plan!r}"
        )
        assert isinstance(plan["is_active"], bool), (
            f"[TC-228:{code}] is_active должен быть bool: {plan!r}"
        )
