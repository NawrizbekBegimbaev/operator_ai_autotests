from __future__ import annotations

import pytest
from playwright.sync_api import Page, Request, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.negative
@pytest.mark.validation
@pytest.mark.auth
def test_tc_006_empty_fields_show_validation_without_login_request(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-006 — пустые поля подсказывают, что нужно заполнить.

    Ожидаемый результат: под полями показаны точные подсказки
    «Введите логин!» и «Введите пароль!»; пользователь остаётся на странице
    входа; запрос POST /v1/auth/login не отправляется.
    """
    login_page = LoginPage(clean_login_page)
    login_requests: list[Request] = []

    def record_login_request(request: Request) -> None:
        if request.method == "POST" and request.url.endswith("/v1/auth/login"):
            login_requests.append(request)

    clean_login_page.on("request", record_login_request)
    login_page.open(test_settings.web_base_url)
    login_page.submit()

    expect(
        login_page.username_validation,
        "[TC-006] под полем логина ожидали точную обязательную подсказку",
    ).to_have_text("Введите логин!")
    expect(
        login_page.password_validation,
        "[TC-006] под полем пароля ожидали точную обязательную подсказку",
    ).to_have_text("Введите пароль!")
    expect(
        clean_login_page,
        "[TC-006] после клиентской валидации ожидали остаться на странице входа",
    ).to_have_url(f"{test_settings.web_base_url}/auth/jwt/sign-in")
    assert login_requests == [], (
        "[TC-006] при пустых полях ожидали 0 запросов POST /v1/auth/login, "
        f"получили {len(login_requests)}"
    )
