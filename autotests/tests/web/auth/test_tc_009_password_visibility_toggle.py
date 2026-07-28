from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.low
@pytest.mark.positive
@pytest.mark.auth
def test_tc_009_password_toggle_shows_and_hides_value(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-009 — кнопка-глазок показывает и повторно скрывает пароль.

    Ожидаемый результат: после первого нажатия введённый пароль отображается
    обычным текстом, после второго снова имеет тип password и остаётся тем же.
    """
    password = "AT-password-123"
    login_page = LoginPage(clean_login_page)

    login_page.open(test_settings.web_base_url)
    login_page.password_input.fill(password)

    expect(
        login_page.show_password_button,
        "[TC-009] перед раскрытием ожидали кнопку «показать»",
    ).to_be_visible()
    login_page.show_password()
    expect(
        login_page.password_input,
        "[TC-009] после первого нажатия ожидали видимый текст пароля",
    ).to_have_attribute("type", "text")
    expect(
        login_page.password_input,
        "[TC-009] раскрытие не должно менять введённый пароль",
    ).to_have_value(password)

    expect(
        login_page.hide_password_button,
        "[TC-009] после раскрытия ожидали кнопку «скрыть»",
    ).to_be_visible()
    login_page.hide_password()
    expect(
        login_page.password_input,
        "[TC-009] после второго нажатия ожидали снова скрытый пароль",
    ).to_have_attribute("type", "password")
    expect(
        login_page.password_input,
        "[TC-009] повторное скрытие не должно менять введённый пароль",
    ).to_have_value(password)
