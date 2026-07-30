from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import APIRequestContext, APIResponse, Page, expect

from autotests.config import Settings
from autotests.pages.operator_calls_page import OperatorCallsPage
from autotests.support.call_api import (
    CallApiContractError,
    get_operator_events_page,
)
from autotests.support.operator_api import list_operators


AuthorizedPageFactory = Callable[[str], Page]


def _display_name(operator: dict[str, Any]) -> str:
    full_name = " ".join(
        str(operator.get(field) or "").strip()
        for field in ("first_name", "last_name")
    ).strip()
    return full_name or str(operator.get("username") or "").strip()


def _two_operators_with_calls(
    rop_request: APIRequestContext,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    operators = list_operators(
        rop_request,
        checkpoint="[TC-365 setup] список операторов",
    )
    for operator in operators:
        operator_id = operator.get("id")
        if not isinstance(operator_id, str) or not operator_id:
            raise CallApiContractError(
                "[TC-365 setup] у оператора нет строкового id: "
                f"{operator!r}"
            )
        page = get_operator_events_page(
            rop_request,
            operator_id,
            checkpoint=f"[TC-365 setup] звонки оператора {operator_id}",
        )
        if page["items"]:
            candidates.append((operator, page))
        if len(candidates) == 2:
            return candidates
    pytest.skip(
        "[TC-365 setup] нужны два оператора с историей звонков"
    )


def _is_operator_events_response(
    response: APIResponse,
    operator_id: str,
) -> bool:
    if (
        response.request.method != "GET"
        or urlsplit(response.url).path != "/v1/onlinepbx/events"
    ):
        return False
    query = parse_qs(urlsplit(response.url).query)
    return query.get("filter") == [f"operator_id='{operator_id}'"]


def _response_items(
    response: APIResponse,
    *,
    checkpoint: str,
) -> list[dict[str, Any]]:
    if response.status != 200:
        raise CallApiContractError(
            f"{checkpoint} ожидали HTTP 200, получили "
            f"{response.status}: {response.text()}"
        )
    body = response.json()
    items = body.get("items") if isinstance(body, dict) else None
    if not isinstance(items, list) or not all(
        isinstance(item, dict) for item in items
    ):
        raise CallApiContractError(
            f"{checkpoint} ожидали JSON-объект с items: {body!r}"
        )
    return items


def _expected_cell(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else "-"


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
def test_tc_365_operator_histories_are_server_scoped(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-365 — история двух операторов не содержит звонков друг друга."""
    candidates = _two_operators_with_calls(rop_api_request)
    page = authorized_page_factory("rop")
    history = OperatorCallsPage(page)
    seen_ids: list[set[str]] = []

    for operator, direct_page in candidates:
        operator_id = str(operator["id"])
        full_name = _display_name(operator)
        with page.expect_response(
            lambda response, expected_id=operator_id: (
                _is_operator_events_response(response, expected_id)
            )
        ) as response_info:
            history.open_for_operator(
                test_settings.web_base_url,
                operator_id,
            )

        response_items = _response_items(
            response_info.value,
            checkpoint=f"[TC-365] UI-ответ оператора {operator_id}",
        )
        direct_ids = {
            str(item.get("id"))
            for item in direct_page["items"]
            if item.get("id")
        }
        response_ids = {
            str(item.get("id"))
            for item in response_items
            if item.get("id")
        }
        assert response_ids == direct_ids, (
            "[TC-365] UI и независимый API-запрос вернули разные звонки "
            f"для оператора {operator_id}: UI={response_ids!r}, "
            f"API={direct_ids!r}"
        )
        assert all(
            item.get("operator_id") == operator_id
            for item in response_items
        ), (
            "[TC-365] серверный фильтр вернул звонок другого оператора: "
            f"{response_items!r}"
        )
        seen_ids.append(response_ids)

        expect(history.heading(full_name)).to_be_visible()
        expect(
            history.data_rows,
            f"[TC-365] ожидали {len(response_items)} строк истории",
        ).to_have_count(len(response_items))
        for index, event in enumerate(response_items):
            cells = history.row_cells(index)
            expect(cells).to_have_count(8)
            expect(cells.nth(1)).to_have_text(
                _expected_cell(event.get("event"))
            )
            expect(cells.nth(2)).to_have_text(
                _expected_cell(event.get("direction"))
            )
            expect(cells.nth(3)).to_have_text(
                _expected_cell(event.get("caller"))
            )
            expect(cells.nth(4)).to_have_text(
                _expected_cell(event.get("callee"))
            )

    assert seen_ids[0].isdisjoint(seen_ids[1]), (
        "[TC-365] один и тот же event id появился в историях двух "
        f"операторов: {seen_ids[0] & seen_ids[1]!r}"
    )
