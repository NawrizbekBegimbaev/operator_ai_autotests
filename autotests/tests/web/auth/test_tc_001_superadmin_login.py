from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage
from autotests.pages.rop_list_page import RopListPage


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.auth
def test_tc_001_superadmin_login(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-001 — вход супер-админа с верными логином и паролем.

    Ожидаемый результат: вход выполнен; открыт адрес /dashboard/rop;
    отображается таблица компаний РОП; в левом меню видны точные пункты
    «РОПы», «Лиды», «Тарифы».
    """
    login_page = LoginPage(clean_login_page)
    rop_list_page = RopListPage(clean_login_page)

    login_page.open(test_settings.web_base_url)
    login_page.sign_in(
        username=test_settings.superadmin_username,
        password=test_settings.superadmin_password,
    )

    expect(
        clean_login_page,
        "[TC-001] после входа ожидали точный адрес /dashboard/rop",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/rop")
    expect(
        rop_list_page.heading,
        "[TC-001] ожидали загруженный раздел «Компании РОП» со счётчиком",
    ).to_have_text(re.compile(r"^Компании РОП · \d+$"))
    expect(
        rop_list_page.companies_table,
        "[TC-001] ожидали видимую таблицу компаний РОП",
    ).to_be_visible()
    expect(
        rop_list_page.rop_menu_link,
        "[TC-001] ожидали пункт меню «РОПы»",
    ).to_have_text("РОПы")
    expect(
        rop_list_page.leads_menu_link,
        "[TC-001] ожидали пункт меню «Лиды»",
    ).to_have_text("Лиды")
    expect(
        rop_list_page.tariffs_menu_link,
        "[TC-001] ожидали пункт меню «Тарифы»",
    ).to_have_text("Тарифы")
