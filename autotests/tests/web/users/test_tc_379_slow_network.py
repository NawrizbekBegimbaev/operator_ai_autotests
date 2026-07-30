from __future__ import annotations

import os
from collections.abc import Callable
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from playwright.sync_api import (
    APIRequestContext,
    CDPSession,
    Page,
    Request,
    expect,
)

from autotests.config import Settings
from autotests.pages.operator_list_page import OperatorListPage
from autotests.support.operator_api import get_operator
from autotests.support.temporary_users import TemporaryOperator


AuthorizedPageFactory = Callable[[str], Page]
NETWORK_LATENCY_MS = int(
    os.getenv("OPERATOR_AI_TC379_LATENCY_MS", "2500")
)
MANUAL_PRE_SAVE_PAUSE_MS = int(
    os.getenv("OPERATOR_AI_TC379_MANUAL_PAUSE_MS", "0")
)
NETWORK_THROUGHPUT_BYTES = 256 * 1024


def _set_slow_network(cdp: CDPSession, *, latency_ms: int) -> None:
    cdp.send(
        "Network.emulateNetworkConditions",
        {
            "offline": False,
            "latency": latency_ms,
            "downloadThroughput": (
                NETWORK_THROUGHPUT_BYTES if latency_ms else -1
            ),
            "uploadThroughput": (
                NETWORK_THROUGHPUT_BYTES if latency_ms else -1
            ),
        },
    )


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.serial
@pytest.mark.xfail(
    reason=(
        "BUG-030: при медленном сохранении форма блокирует кнопку, "
        "но не показывает понятный индикатор загрузки"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_379_slow_save_shows_progress_and_sends_one_patch(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    temporary_operator: TemporaryOperator,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-379 — медленный ответ виден, а повторный клик не дублирует PATCH."""
    page = authorized_page_factory("rop")
    operator_list = OperatorListPage(page)
    operator_list.open(test_settings.web_base_url)

    original_row = operator_list.row_by_full_name(
        temporary_operator.first_name,
        temporary_operator.last_name,
    )
    try:
        expect(
            original_row,
            "[TC-379 setup] временный оператор должен быть в свежем списке",
        ).to_have_count(1, timeout=10_000)
    except AssertionError:
        page.reload(wait_until="domcontentloaded")
        original_row = operator_list.row_by_full_name(
            temporary_operator.first_name,
            temporary_operator.last_name,
        )
        expect(
            original_row,
            "[TC-379 setup] временный оператор должен появиться после reload",
        ).to_have_count(1, timeout=15_000)

    dialog = operator_list.open_edit_dialog(
        temporary_operator.first_name,
        temporary_operator.last_name,
    )
    expect(
        dialog.dialog,
        "[TC-379] ожидали форму редактирования временного оператора",
    ).to_be_visible()
    expect(dialog.first_name_input).to_have_value(
        temporary_operator.first_name
    )
    expect(dialog.last_name_input).to_have_value(temporary_operator.last_name)
    expect(dialog.username_input).to_have_value(temporary_operator.username)

    updated_first_name = f"Slow{uuid4().hex[:7]}"
    dialog.first_name_input.fill(updated_first_name)
    expect(
        dialog.save_button,
        "[TC-379] валидная форма должна разрешать сохранение",
    ).to_be_enabled()

    target_path = f"/v1/users/{temporary_operator.id}"
    patch_requests: list[Request] = []

    def remember_target_patch(request: Request) -> None:
        if (
            request.method == "PATCH"
            and urlsplit(request.url).path == target_path
        ):
            patch_requests.append(request)

    page.on("request", remember_target_patch)
    cdp = page.context.new_cdp_session(page)
    cdp.send("Network.enable")

    try:
        _set_slow_network(cdp, latency_ms=NETWORK_LATENCY_MS)
        page.bring_to_front()
        if MANUAL_PRE_SAVE_PAUSE_MS:
            page.wait_for_timeout(MANUAL_PRE_SAVE_PAUSE_MS)

        with page.expect_response(
            lambda response: (
                response.request.method == "PATCH"
                and urlsplit(response.url).path == target_path
            ),
            timeout=max(15_000, NETWORK_LATENCY_MS * 3),
        ) as response_info:
            dialog.save_button.click()
            expect(
                dialog.save_button,
                "[TC-379] во время ожидания кнопка должна блокировать повтор",
            ).to_be_disabled(timeout=1_000)
            has_loading_indicator = dialog.has_visible_loading_indicator()

            # Нативный click по disabled-кнопке имитирует повторное нажатие,
            # не обходя защиту браузера через принудительный Playwright click.
            dialog.save_button.evaluate("(button) => button.click()")

        patch_response = response_info.value
    finally:
        _set_slow_network(cdp, latency_ms=0)
        cdp.detach()

    assert patch_response.status == 200, (
        "[TC-379] при сохранении ожидали HTTP 200, получили "
        f"{patch_response.status}: {patch_response.text()}"
    )
    assert len(patch_requests) == 1, (
        "[TC-379] повторное нажатие должно отправить один PATCH, получено "
        f"{len(patch_requests)}"
    )

    expect(
        page.get_by_role("alert").filter(has_text="Пользователь сохранён"),
        "[TC-379] после ответа ожидали подтверждение сохранения",
    ).to_be_visible()
    expect(
        operator_list.row_by_full_name(
            updated_first_name,
            temporary_operator.last_name,
        ),
        "[TC-379] таблица должна показать подтверждённое сервером имя",
    ).to_have_count(1)

    saved = get_operator(
        rop_api_request,
        temporary_operator.id,
        checkpoint="[TC-379] проверка через API",
    )
    assert saved.get("first_name") == updated_first_name, (
        "[TC-379] API не сохранил новое имя: "
        f"ожидали {updated_first_name!r}, получили {saved.get('first_name')!r}"
    )
    assert saved.get("last_name") == temporary_operator.last_name, (
        "[TC-379] неизменённая фамилия была потеряна: "
        f"{saved.get('last_name')!r}"
    )
    assert saved.get("username") == temporary_operator.username, (
        "[TC-379] неизменённый username был потерян: "
        f"{saved.get('username')!r}"
    )
    assert has_loading_indicator, (
        f"[TC-379] при задержке ответа {NETWORK_LATENCY_MS / 1000:g} секунды "
        "форма блокирует кнопку, "
        "но не показывает progressbar, aria-busy или текст ожидания"
    )
