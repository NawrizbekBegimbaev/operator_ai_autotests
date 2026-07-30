from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, Request, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage
from autotests.support.login_rate_guard import LoginRateGuard


@pytest.mark.web
@pytest.mark.low
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.serial
def test_tc_020_double_click_sends_one_login_request(
    clean_login_page: Page,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> None:
    """TC-020 — двойной клик выполняет один обычный вход без ошибки."""
    credentials = test_settings.credentials_for("rop")
    login_page = LoginPage(clean_login_page)
    login_requests: list[Request] = []

    def remember_login_request(request: Request) -> None:
        if (
            request.method == "POST"
            and urlsplit(request.url).path == "/v1/auth/login"
        ):
            login_requests.append(request)

    clean_login_page.on("request", remember_login_request)
    login_page.open(test_settings.web_base_url)
    login_page.username_input.fill(credentials.username)
    login_page.password_input.fill(credentials.password)

    login_rate_guard.before_attempt()
    login_page.submit_button.dblclick(delay=20)

    expect(
        clean_login_page,
        "[TC-020] после двойного клика ожидали обычный вход РОП",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/dynamic-form")
    assert len(login_requests) == 1, (
        "[TC-020] двойной клик должен отправить ровно один POST /v1/auth/login, "
        f"получили {len(login_requests)} запросов"
    )
    expect(
        login_page.error_alert,
        "[TC-020] после успешного двойного клика не должно быть ошибки входа",
    ).to_have_count(0)
