from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import APIResponse, Page, expect

from autotests.config import Settings
from autotests.pages.operator_deals_page import (
    OperatorDealDetailsPage,
    OperatorDealsPage,
)


AuthorizedPageFactory = Callable[[str], Page]


def _is_deals_list_response(response: APIResponse) -> bool:
    return (
        response.request.method == "GET"
        and urlsplit(response.url).path == "/v1/amocrm/deals"
    )


def _collection_items(body: Any) -> list[dict[str, Any]]:
    candidates: Any = body
    if isinstance(body, dict):
        candidates = body.get("items")
        if not isinstance(candidates, list):
            candidates = body.get("results")
        if not isinstance(candidates, list):
            candidates = body.get("data")
        if isinstance(candidates, dict):
            candidates = candidates.get("items")
    if not isinstance(candidates, list):
        return []
    return [item for item in candidates if isinstance(item, dict)]


def _status_name(deal: dict[str, Any]) -> str:
    status = deal.get("status")
    if not isinstance(status, dict):
        return ""
    name = status.get("name")
    return str(name).strip() if name not in (None, "") else ""


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
def test_tc_065_operator_deals_show_status_attempts_and_details(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """TC-065 — список и карточка рабочего лида относятся к одной сделке."""
    page = authorized_page_factory("operator")
    deals_page = OperatorDealsPage(page)

    with page.expect_response(_is_deals_list_response) as list_response_info:
        deals_page.open(test_settings.web_base_url)

    list_response = list_response_info.value
    assert list_response.status == 200, (
        "[TC-065] при загрузке сделок ожидали 200, получили "
        f"{list_response.status}: {list_response.text()}"
    )
    items = _collection_items(list_response.json())
    visible_items = [
        item
        for item in items
        if isinstance(item.get("id"), str)
        and item.get("id")
        and isinstance(item.get("name"), str)
        and item.get("name")
    ]
    if not visible_items:
        pytest.skip(
            "[TC-065 setup] у тестового оператора нет рабочих лидов"
        )

    deal = visible_items[0]
    deal_id = str(deal["id"])
    deal_name = str(deal["name"])
    expect(
        deals_page.heading,
        "[TC-065] ожидали раздел «Звонки»",
    ).to_be_visible()
    expect(deals_page.column_headers).to_have_text(
        [
            "Название сделки",
            "Статус",
            "Попытки",
            "Последний звонок",
            "Действие",
        ]
    )
    expect(
        deals_page.data_rows,
        "[TC-065] число строк должно совпадать с ответом API",
    ).to_have_count(len(visible_items))

    first_row_cells = deals_page.row_cells(0)
    expect(first_row_cells).to_have_count(5)
    expect(first_row_cells.nth(0)).to_contain_text(deal_name)

    contact_phone = str(deal.get("contact_phone") or "").strip()
    if contact_phone:
        expect(first_row_cells.nth(0)).to_contain_text(contact_phone)

    expected_status = _status_name(deal) or "-"
    expect(first_row_cells.nth(1)).to_have_text(expected_status)

    attempts = deal.get("attempts_count")
    expected_attempts = (
        f"{attempts} раз"
        if isinstance(attempts, (int, float)) and attempts
        else "-"
    )
    expect(first_row_cells.nth(2)).to_have_text(expected_attempts)

    last_call_source = (
        deal.get("last_call_at")
        or deal.get("updated_at_amo")
        or deal.get("updated_at")
    )
    if last_call_source:
        expect(first_row_cells.nth(3)).not_to_have_text("-")
    else:
        expect(first_row_cells.nth(3)).to_have_text("-")

    expected_details_path = f"/v1/amocrm/deals/{deal_id}"
    with page.expect_response(
        lambda response: (
            response.request.method == "GET"
            and urlsplit(response.url).path == expected_details_path
        )
    ) as detail_response_info:
        first_row_cells.nth(0).click()

    page.wait_for_url(f"**/dashboard/calls/{deal_id}")
    detail_response = detail_response_info.value
    assert detail_response.status == 200, (
        "[TC-065] при открытии карточки сделки ожидали 200, получили "
        f"{detail_response.status}: {detail_response.text()}"
    )
    detail_body = detail_response.json()
    assert isinstance(detail_body, dict), (
        f"[TC-065] ожидали JSON-объект сделки, получили {detail_body!r}"
    )
    assert detail_body.get("id") == deal_id, (
        "[TC-065] карточка загрузила другую сделку: "
        f"ожидали {deal_id!r}, получили {detail_body!r}"
    )

    details_page = OperatorDealDetailsPage(page)
    expect(details_page.heading).to_be_visible()
    expect(details_page.deal_data_heading).to_be_visible()
    expect(page.get_by_text(deal_name, exact=True).first).to_be_visible()
    if expected_status != "-":
        expect(page.get_by_text(expected_status, exact=True).first).to_be_visible()

    details_page.back_button.click()
    expect(page).to_have_url(
        f"{test_settings.web_base_url}{OperatorDealsPage.PATH}"
    )
