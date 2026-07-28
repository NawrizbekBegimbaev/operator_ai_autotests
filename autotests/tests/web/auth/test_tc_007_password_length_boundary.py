from __future__ import annotations

from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage
from autotests.support.network import track_requests


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.negative
@pytest.mark.validation
@pytest.mark.boundary
@pytest.mark.auth
@pytest.mark.xfail(
    reason=(
        "BUG-020: frontend отправляет пароль из 6 символов, но API отклоняет "
        "его своей границей 8 и UI показывает «validation failed»"
    ),
    strict=True,
)
def test_tc_007_password_length_boundary_controls_submission(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-007 — пароль из 5 символов не отправляется, из 6 отправляется.

    Ожидаемый результат: для 5 символов показано точное сообщение
    «Пароль должен содержать не менее 6 символов!», POST /v1/auth/login
    не отправляется; для 6 символов подсказка исчезает, отправляется ровно
    один запрос и показывается обычная ошибка «login yoki parol noto'g'ri».
    """
    login_page = LoginPage(clean_login_page)
    login_requests = track_requests(
        clean_login_page,
        method="POST",
        url_suffix="/v1/auth/login",
    )

    login_page.open(test_settings.web_base_url)
    login_page.username_input.fill(f"AT-{uuid4().hex[:8]}")
    login_page.password_input.fill("12345")
    login_page.submit()

    expect(
        login_page.password_validation,
        "[TC-007] для 5 символов ожидали точную подсказку минимальной длины",
    ).to_have_text("Пароль должен содержать не менее 6 символов!")
    expect(
        clean_login_page,
        "[TC-007] после клиентской ошибки ожидали остаться на странице входа",
    ).to_have_url(f"{test_settings.web_base_url}/auth/jwt/sign-in")
    assert login_requests == [], (
        "[TC-007] для пароля из 5 символов ожидали 0 запросов "
        f"POST /v1/auth/login, получили {len(login_requests)}"
    )

    login_page.password_input.fill("123456")
    login_page.submit()

    expect(
        login_page.password_validation,
        "[TC-007] для 6 символов ожидали отсутствие ошибки минимальной длины",
    ).to_have_count(0)
    expect(
        login_page.error_alert,
        "[TC-007] после отправки 6 символов ожидали обычную ошибку входа",
    ).to_have_text("login yoki parol noto'g'ri")
    expect(
        clean_login_page,
        "[TC-007] после отклонённого сервером входа ожидали страницу входа",
    ).to_have_url(f"{test_settings.web_base_url}/auth/jwt/sign-in")
    assert len(login_requests) == 1, (
        "[TC-007] для пароля из 6 символов ожидали ровно 1 запрос "
        f"POST /v1/auth/login, получили {len(login_requests)}"
    )
