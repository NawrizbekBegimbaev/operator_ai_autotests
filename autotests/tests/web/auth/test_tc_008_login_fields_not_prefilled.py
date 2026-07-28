from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
def test_tc_008_login_fields_are_empty_in_clean_context(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-008 — поля входа не содержат предзаполненных учётных данных.

    Ожидаемый результат: в новом чистом контексте логин и пароль пустые;
    показаны точные плейсхолдеры «логин» и «6+ символов»; пароль скрыт.
    """
    login_page = LoginPage(clean_login_page)

    login_page.open(test_settings.web_base_url)

    expect(
        login_page.username_input,
        "[TC-008] ожидали пустое поле логина",
    ).to_have_value("")
    expect(
        login_page.password_input,
        "[TC-008] ожидали пустое поле пароля",
    ).to_have_value("")
    expect(
        login_page.username_input,
        "[TC-008] ожидали точный плейсхолдер логина",
    ).to_have_attribute("placeholder", "логин")
    expect(
        login_page.password_input,
        "[TC-008] ожидали точный плейсхолдер минимальной длины пароля",
    ).to_have_attribute("placeholder", "6+ символов")
    expect(
        login_page.password_input,
        "[TC-008] пустое поле пароля ожидали скрытым",
    ).to_have_attribute("type", "password")
