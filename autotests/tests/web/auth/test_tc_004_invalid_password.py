from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
def test_tc_004_invalid_password_rejected(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-004 — вход с неверным паролем не пускает в систему.

    Ожидаемый результат: вход не выполнен; пользователь остаётся на точном
    адресе /auth/jwt/sign-in; над формой показан красный alert с универсальным
    сообщением «login yoki parol noto'g'ri»; пароль остаётся скрытым.
    """
    login_page = LoginPage(clean_login_page)
    wrong_password = f"{test_settings.superadmin_password}x"

    login_page.open(test_settings.web_base_url)
    login_page.sign_in(
        username=test_settings.superadmin_username,
        password=wrong_password,
    )

    expect(
        clean_login_page,
        "[TC-004] после неверного пароля ожидали остаться на странице входа",
    ).to_have_url(f"{test_settings.web_base_url}/auth/jwt/sign-in")
    expect(
        login_page.error_alert,
        "[TC-004] ожидали видимую плашку ошибки над формой",
    ).to_be_visible()
    expect(
        login_page.error_alert,
        "[TC-004] ожидали универсальное сообщение без раскрытия существования логина",
    ).to_have_text("login yoki parol noto'g'ri")
    expect(
        login_page.error_alert,
        "[TC-004] ожидали красную плашку severity=error",
    ).to_have_class(re.compile(r"\bMuiAlert-colorError\b"))
    expect(
        login_page.password_input,
        "[TC-004] после ошибки ожидали скрытое поле пароля",
    ).to_have_attribute("type", "password")
