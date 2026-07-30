from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from playwright.sync_api import APIRequestContext, Page

from autotests.config import Settings
from autotests.pages.operator_detail_page import OperatorDetailPage
from autotests.support.call_api import (
    CallApiContractError,
    event_audio_url,
    list_operator_events,
)
from autotests.support.operator_api import list_operators


AuthorizedPageFactory = Callable[[str], Page]


def _operator_with_recent_audio(
    rop_request: APIRequestContext,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    operators = list_operators(
        rop_request,
        checkpoint="[TC-370 setup] список операторов",
    )
    for operator in operators:
        operator_id = operator.get("id")
        if not isinstance(operator_id, str) or not operator_id:
            raise CallApiContractError(
                "[TC-370 setup] у оператора нет строкового id: "
                f"{operator!r}"
            )
        events = list_operator_events(
            rop_request,
            operator_id,
            checkpoint=f"[TC-370 setup] звонки оператора {operator_id}",
        )
        for event in events:
            if event_audio_url(event):
                return operator, event, 0
    pytest.skip(
        "[TC-370 setup] в последних звонках операторов нет HTTP(S)-аудио"
    )


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.xfail(
    reason=(
        "BUG-026: запись звонка не запускается; Chromium возвращает "
        "MEDIA_ERR_SRC_NOT_SUPPORTED"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_370_operator_card_audio_plays_and_pauses(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-370 — запись в карточке запускается и ставится на паузу."""
    operator, _, audio_index = _operator_with_recent_audio(rop_api_request)
    operator_id = str(operator["id"])

    page = authorized_page_factory("rop")
    detail = OperatorDetailPage(page)
    detail.open(test_settings.web_base_url, operator_id)
    detail.call_recordings_card.wait_for(state="visible")
    play_button = detail.audio_button(audio_index)
    audio = detail.audio_element(audio_index)
    play_button.wait_for(state="visible")
    audio.wait_for(state="attached")

    play_button.click()
    page.wait_for_timeout(3_000)
    playing_state = audio.evaluate(
        """element => ({
            paused: element.paused,
            currentTime: element.currentTime,
            readyState: element.readyState,
            errorCode: element.error ? element.error.code : null
        })"""
    )
    assert (
        isinstance(playing_state, dict)
        and playing_state.get("paused") is False
        and float(playing_state.get("currentTime") or 0) > 0
    ), (
        "[TC-370] после Play запись должна воспроизводиться и продвинуться "
        f"по времени, получено состояние {playing_state!r}"
    )

    play_button.click()
    page.wait_for_timeout(250)
    assert audio.evaluate("element => element.paused") is True, (
        "[TC-370] повторное нажатие должно поставить запись на паузу"
    )
