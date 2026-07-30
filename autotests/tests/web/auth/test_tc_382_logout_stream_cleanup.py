from __future__ import annotations

import re
import time
from collections.abc import Callable
from urllib.parse import urljoin, urlsplit

import pytest
from playwright.sync_api import Page, Request, Response, expect

from autotests.config import Settings
from autotests.pages.account_menu import AccountMenu
from autotests.pages.login_page import LoginPage


AuthorizedPageFactory = Callable[[str], Page]
STREAM_PATH = "/v1/amocrm/deals/stream"
AFTER_LOGOUT_FLAG = "__qa_tc382_after_logout"

PROTECTED_DOM_OBSERVER = f"""
    const scanProtectedContent = () => {{
        if (sessionStorage.getItem("{AFTER_LOGOUT_FLAG}") !== "1") {{
            return;
        }}
        const hasTable = Boolean(document.querySelector('[role="table"]'));
        const text = document.body?.innerText ?? "";
        if (hasTable || text.includes("Название сделки")) {{
            window.__qaRecordTc382ProtectedContent();
        }}
    }};
    new MutationObserver(scanProtectedContent).observe(document, {{
        childList: true,
        subtree: true,
        characterData: true
    }});
    document.addEventListener("DOMContentLoaded", scanProtectedContent);
"""


def _is_stream_request(request: Request) -> bool:
    return urlsplit(request.url).path == STREAM_PATH


def _wait_until(
    page: Page,
    predicate: Callable[[], bool],
    *,
    checkpoint: str,
    timeout_ms: int = 5_000,
) -> None:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        if predicate():
            return
        page.wait_for_timeout(50)
    raise AssertionError(f"{checkpoint} условие не выполнено за {timeout_ms} ms")


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.security
@pytest.mark.auth
@pytest.mark.xfail(
    reason=(
        "BUG-029: GET /v1/amocrm/deals/stream не возвращает HTTP headers, "
        "initial snapshot или keepalive на staging"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_382_logout_closes_stream_and_does_not_restore_cached_data(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """
    TC-382 — logout закрывает SSE и не возвращает кэш кабинета.

    Новое событие и вход пользователем второй компании не выполняются:
    для них нужны отдельные согласованные данные. Текущая автоматическая часть
    не изменяет staging.
    """
    page = authorized_page_factory("operator")
    account_menu = AccountMenu(page)
    login_page = LoginPage(page)
    stream_requests: list[Request] = []
    active_streams: set[Request] = set()
    stream_responses: list[Response] = []
    stream_failures: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    protected_content_after_logout: list[str] = []

    page.expose_binding(
        "__qaRecordTc382ProtectedContent",
        lambda _source: protected_content_after_logout.append(
            "защищённая таблица"
        ),
    )
    page.add_init_script(script=PROTECTED_DOM_OBSERVER)

    def remember_request(request: Request) -> None:
        if not _is_stream_request(request):
            return
        stream_requests.append(request)
        active_streams.add(request)

    def remember_finished_request(request: Request) -> None:
        if _is_stream_request(request):
            active_streams.discard(request)

    def remember_failed_request(request: Request) -> None:
        if not _is_stream_request(request):
            return
        active_streams.discard(request)
        stream_failures.append(request.failure or "network failure")

    def remember_stream_response(response: Response) -> None:
        if _is_stream_request(response.request):
            stream_responses.append(response)

    page.on("request", remember_request)
    page.on("requestfinished", remember_finished_request)
    page.on("requestfailed", remember_failed_request)
    page.on("response", remember_stream_response)
    page.on(
        "console",
        lambda message: (
            console_errors.append(message.text)
            if message.type == "error"
            else None
        ),
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    page.goto(
        urljoin(f"{test_settings.web_base_url}/", "dashboard/calls"),
        wait_until="domcontentloaded",
    )
    expect(
        page.get_by_role("heading", name="Звонки", exact=True),
        "[TC-382] ожидали открытый раздел звонков",
    ).to_be_visible()
    expect(
        page.get_by_role("table"),
        "[TC-382] ожидали таблицу данных кабинета",
    ).to_be_visible()

    _wait_until(
        page,
        lambda: bool(stream_responses),
        checkpoint="[TC-382] ожидали ответ SSE",
        timeout_ms=10_000,
    )
    first_stream_response = stream_responses[0]
    assert first_stream_response.status == 200, (
        "[TC-382] SSE должен открыться с HTTP 200, получено "
        f"{first_stream_response.status}"
    )
    assert first_stream_response.headers.get("content-type", "").startswith(
        "text/event-stream"
    ), (
        "[TC-382] ожидали Content-Type text/event-stream, получили "
        f"{first_stream_response.headers.get('content-type')!r}"
    )
    assert active_streams, (
        "[TC-382] после открытия раздела SSE должен оставаться активным"
    )

    account_menu.open()
    expect(account_menu.logout_button).to_be_visible()
    account_menu.logout()

    expect(
        page,
        "[TC-382] после logout ожидали страницу входа",
    ).to_have_url(
        re.compile(
            rf"^{re.escape(test_settings.web_base_url)}"
            rf"{re.escape(LoginPage.SIGN_IN_PATH)}(?:\?.*)?$"
        )
    )
    expect(login_page.username_input).to_be_visible()

    _wait_until(
        page,
        lambda: not active_streams,
        checkpoint="[TC-382] logout должен закрыть SSE",
    )
    stream_count_after_close = len(stream_requests)
    page.wait_for_timeout(1_000)
    assert len(stream_requests) == stream_count_after_close, (
        "[TC-382] после logout не должен запускаться новый SSE; "
        f"было {stream_count_after_close}, стало {len(stream_requests)}"
    )

    session_state = page.evaluate(
        """() => ({
            localToken: localStorage.getItem('jwt_access_token'),
            sessionToken: sessionStorage.getItem('jwt_access_token'),
            localUser: localStorage.getItem('jwt_user'),
            sessionUser: sessionStorage.getItem('jwt_user')
        })"""
    )
    assert session_state == {
        "localToken": None,
        "sessionToken": None,
        "localUser": None,
        "sessionUser": None,
    }, (
        "[TC-382] logout должен удалить токен и пользователя из browser "
        f"storage, получено {session_state!r}"
    )

    page.evaluate(
        f"""() => sessionStorage.setItem("{AFTER_LOGOUT_FLAG}", "1")"""
    )
    page.go_back()
    expect(
        page,
        "[TC-382] browser Back не должен возвращать кабинет",
    ).to_have_url(
        re.compile(
            rf"^{re.escape(test_settings.web_base_url)}"
            rf"{re.escape(LoginPage.SIGN_IN_PATH)}(?:\?.*)?$"
        )
    )
    expect(login_page.username_input).to_be_visible()
    expect(page.get_by_role("table")).to_have_count(0)

    page.reload(wait_until="domcontentloaded")
    expect(login_page.username_input).to_be_visible()
    expect(page.get_by_role("table")).to_have_count(0)

    assert not protected_content_after_logout, (
        "[TC-382] после logout защищённый DOM появился при Back/reload; "
        f"количество наблюдений={len(protected_content_after_logout)}"
    )
    assert not console_errors, (
        "[TC-382] во время logout/закрытия SSE появились Console Error; "
        f"количество={len(console_errors)}"
    )
    assert not page_errors, (
        "[TC-382] обнаружены необработанные JavaScript-ошибки; "
        f"количество={len(page_errors)}"
    )
    assert stream_failures in ([], ["net::ERR_ABORTED"]), (
        "[TC-382] SSE должен завершиться штатно или через AbortController, "
        f"получено {stream_failures!r}"
    )
