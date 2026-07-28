from __future__ import annotations

import re
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.account_menu import AccountMenu
from autotests.pages.login_page import LoginPage
from autotests.pages.rop_list_page import RopListPage


def assert_signed_out(
    page: Page,
    *,
    login_page: LoginPage,
    rop_list_page: RopListPage,
    expected_base_url: str,
    checkpoint: str,
) -> None:
    expected_url = urlsplit(
        f"{expected_base_url}{LoginPage.SIGN_IN_PATH}"
    )
    expect(
        page,
        f"[TC-010] {checkpoint}: ожидали страницу входа",
    ).to_have_url(
        re.compile(
            rf"^{re.escape(expected_base_url)}"
            rf"{re.escape(LoginPage.SIGN_IN_PATH)}(?:\?.*)?$"
        )
    )
    actual_url = urlsplit(page.url)
    assert (
        actual_url.scheme,
        actual_url.netloc,
        actual_url.path,
    ) == (
        expected_url.scheme,
        expected_url.netloc,
        expected_url.path,
    ), (
        f"[TC-010] {checkpoint}: ожидали origin и path "
        f"{expected_base_url}{LoginPage.SIGN_IN_PATH}, получили {page.url}"
    )
    expect(
        login_page.username_input,
        f"[TC-010] {checkpoint}: ожидали видимую форму входа",
    ).to_be_visible()
    expect(
        rop_list_page.companies_table,
        f"[TC-010] {checkpoint}: защищённая таблица не должна присутствовать",
    ).to_have_count(0)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.auth
def test_tc_010_logout_blocks_back_navigation_and_reload(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-010 — выход завершает сессию.

    Ожидаемый результат: после «Выйти» открывается точная страница входа;
    после browser Back и после обновления защищённый кабинет не открывается,
    снова видна форма входа, а таблица компаний РОП отсутствует.
    """
    login_page = LoginPage(clean_login_page)
    rop_list_page = RopListPage(clean_login_page)
    account_menu = AccountMenu(clean_login_page)

    login_page.open(test_settings.web_base_url)
    login_page.sign_in(
        username=test_settings.superadmin_username,
        password=test_settings.superadmin_password,
    )
    expect(
        clean_login_page,
        "[TC-010] предусловие: ожидали успешный собственный вход супер-админа",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/rop")

    account_menu.open()
    expect(
        account_menu.logout_button,
        "[TC-010] в меню аккаунта ожидали точную кнопку «Выйти»",
    ).to_be_visible()
    account_menu.logout()

    assert_signed_out(
        clean_login_page,
        login_page=login_page,
        rop_list_page=rop_list_page,
        expected_base_url=test_settings.web_base_url,
        checkpoint="после выхода",
    )

    account_menu.go_back()

    assert_signed_out(
        clean_login_page,
        login_page=login_page,
        rop_list_page=rop_list_page,
        expected_base_url=test_settings.web_base_url,
        checkpoint="после browser Back",
    )

    account_menu.reload()

    assert_signed_out(
        clean_login_page,
        login_page=login_page,
        rop_list_page=rop_list_page,
        expected_base_url=test_settings.web_base_url,
        checkpoint="после обновления",
    )
