from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from autotests.config import Settings
from autotests.pages.call_transcript_page import CallTranscriptPage
from autotests.pages.operator_detail_page import OperatorDetailPage
from autotests.support.call_api import (
    CallApiContractError,
    get_event,
    list_operator_events,
)
from autotests.support.operator_api import list_operators


AuthorizedPageFactory = Callable[[str], Page]


def _operator_event_without_deal(
    rop_request: APIRequestContext,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    operators = list_operators(
        rop_request,
        checkpoint="[TC-060 call-details setup] список операторов",
    )
    for operator in operators:
        operator_id = operator.get("id")
        if not isinstance(operator_id, str) or not operator_id:
            raise CallApiContractError(
                "[TC-060 call-details setup] у оператора нет строкового id: "
                f"{operator!r}"
            )
        events = list_operator_events(
            rop_request,
            operator_id,
            checkpoint=(
                "[TC-060 call-details setup] последние звонки "
                f"оператора {operator_id}"
            ),
        )
        for index, event in enumerate(events):
            event_id = event.get("id")
            deal_id = event.get("deal_id")
            if (
                isinstance(event_id, str)
                and event_id
                and not (isinstance(deal_id, str) and deal_id.strip())
            ):
                return operator, event, index
    pytest.skip(
        "[TC-060 call-details setup] среди последних звонков нет события "
        "без deal_id для воспроизведения BUG-027"
    )


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.positive
@pytest.mark.xfail(
    reason=(
        "BUG-027: переход из карточки по звонку без deal_id фильтрует "
        "события по его event id и открывает пустую страницу"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_060_selected_call_opens_with_its_data(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-060 — выбранная запись открывает данные именно этого звонка."""
    operator, event, event_index = _operator_event_without_deal(
        rop_api_request
    )
    operator_id = str(operator["id"])
    event_id = str(event["id"])
    stored_event = get_event(
        rop_api_request,
        event_id,
        checkpoint="[TC-060 call-details setup] прямое чтение события",
    )
    expected_event_name = str(stored_event.get("event") or "").strip()
    if not expected_event_name:
        raise CallApiContractError(
            "[TC-060 call-details setup] у сохранённого события нет event: "
            f"{stored_event!r}"
        )

    page = authorized_page_factory("rop")
    operator_detail = OperatorDetailPage(page)
    operator_detail.open(test_settings.web_base_url, operator_id)
    operator_detail.call_recordings_card.wait_for(state="visible")
    call_title = operator_detail.call_title(event_index)
    call_title.wait_for(state="visible")

    with page.expect_response(
        lambda response: (
            response.request.method == "GET"
            and urlsplit(response.url).path == "/v1/onlinepbx/events"
            and "filter=" in urlsplit(response.url).query
        )
    ) as details_response_info:
        call_title.click()

    page.wait_for_url(
        f"**/dashboard/calls/{event_id}/transcript/{event_id}"
    )
    details_response = details_response_info.value
    if details_response.status not in {200, 404}:
        raise CallApiContractError(
            "[TC-060 call-details] запрос списка событий вернул "
            f"{details_response.status}: {details_response.text()}"
        )
    details_body = details_response.json()
    if not isinstance(details_body, dict):
        raise CallApiContractError(
            "[TC-060 call-details] UI получил неожиданный контракт: "
            f"{details_body!r}"
        )
    if details_response.status == 200 and not isinstance(
        details_body.get("items"), list
    ):
        raise CallApiContractError(
            "[TC-060 call-details] успешный UI-ответ не содержит items: "
            f"{details_body!r}"
        )

    transcript = CallTranscriptPage(page)
    transcript.heading.wait_for(state="visible")
    expect(
        transcript.detail_value("Событие"),
        (
            "[TC-060 call-details] страница должна показать событие "
            f"{expected_event_name!r} с id={event_id}"
        ),
    ).to_have_text(expected_event_name)
