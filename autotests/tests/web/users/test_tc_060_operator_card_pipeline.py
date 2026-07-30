from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from autotests.config import Settings
from autotests.pages.operator_detail_page import OperatorDetailPage
from autotests.support.operator_api import (
    OperatorApiContractError,
    list_operator_pipelines,
    list_operators,
)


AuthorizedPageFactory = Callable[[str], Page]


def _candidate_with_pipeline(
    rop_request: APIRequestContext,
) -> tuple[dict[str, Any], dict[str, Any]]:
    operators = list_operators(
        rop_request,
        checkpoint="[TC-060 setup] список операторов",
    )
    for operator in operators:
        operator_id = operator.get("id")
        if not isinstance(operator_id, str) or not operator_id:
            raise OperatorApiContractError(
                "[TC-060 setup] у оператора отсутствует строковый id: "
                f"{operator!r}"
            )
        assignments = list_operator_pipelines(
            rop_request,
            operator_id,
            checkpoint=f"[TC-060 setup] воронки оператора {operator_id}",
        )
        for assignment in assignments:
            pipeline_name = assignment.get("pipeline_name")
            if isinstance(pipeline_name, str) and pipeline_name.strip():
                return operator, assignment
    pytest.skip(
        "[TC-060 setup] у доступных РОПу операторов нет назначенной воронки"
    )


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.xfail(
    reason=(
        "BUG-024: карточка оператора не показывает назначенную воронку, "
        "потому что frontend читает ответ {items: [...]} как массив"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_060_operator_card_shows_assigned_pipeline(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-060 — карточка показывает назначенную оператору воронку."""
    operator, assignment = _candidate_with_pipeline(rop_api_request)
    operator_id = str(operator["id"])
    pipeline_name = str(assignment["pipeline_name"]).strip()
    full_name = " ".join(
        str(operator.get(field) or "").strip()
        for field in ("first_name", "last_name")
    ).strip()
    if not full_name:
        full_name = str(operator.get("username") or "").strip()
    if not full_name:
        raise OperatorApiContractError(
            f"[TC-060 setup] у оператора нет отображаемого имени: {operator!r}"
        )

    page = authorized_page_factory("rop")
    detail = OperatorDetailPage(page)
    with page.expect_response(
        lambda response: (
            response.request.method == "GET"
            and urlsplit(response.url).path == "/v1/operator-pipelines"
            and f"operator_id={operator_id}" in response.url
        )
    ) as pipeline_response_info:
        detail.open(test_settings.web_base_url, operator_id)

    pipeline_response = pipeline_response_info.value
    if pipeline_response.status != 200:
        raise OperatorApiContractError(
            "[TC-060] UI-запрос назначений вернул "
            f"{pipeline_response.status}: {pipeline_response.text()}"
        )
    response_body = pipeline_response.json()
    response_items = (
        response_body.get("items")
        if isinstance(response_body, dict)
        else None
    )
    if not isinstance(response_items, list):
        raise OperatorApiContractError(
            "[TC-060] UI получил неожиданный контракт назначений: "
            f"{response_body!r}"
        )
    if not any(
        isinstance(item, dict)
        and item.get("operator_id") == operator_id
        and item.get("pipeline_name") == pipeline_name
        for item in response_items
    ):
        raise OperatorApiContractError(
            "[TC-060] UI-ответ не содержит выбранное назначение: "
            f"{response_body!r}"
        )

    detail.operator_heading(full_name).wait_for(state="visible")
    expect(
        detail.pipeline_label(pipeline_name),
        (
            "[TC-060] рядом с именем должна отображаться метка "
            f"«Воронка: {pipeline_name}»"
        ),
    ).to_be_visible()
