from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.deployment_smoke_page import DeploymentSmokePage
from autotests.pages.login_page import LoginPage
from autotests.support.login_rate_guard import LoginRateGuard


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.auth
def test_tc_375_clean_session_loads_current_deployment_resources(
    clean_login_page: Page,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> None:
    """
    TC-375 — чистая сессия загружает актуальные JS/CSS основных маршрутов.

    Автоматизирована проверка текущего деплоя в новом browser context и после
    reload. Настоящая вкладка, открытая до следующего деплоя, проверяется
    отдельно во время релизной приёмки.
    """
    page = clean_login_page
    deployment_page = DeploymentSmokePage(page)
    login_page = LoginPage(page)
    credentials = test_settings.credentials_for("operator")

    login_page.open(test_settings.web_base_url)
    login_rate_guard.before_attempt()
    login_page.sign_in(
        username=credentials.username,
        password=credentials.password,
    )

    home_url = f"{test_settings.web_base_url}/dashboard/home"
    expect(
        page,
        "[TC-375] чистый вход оператора должен открыть рабочий стол",
    ).to_have_url(home_url)

    sections = (
        ("Режим звонков", "/dashboard/calling", "Обзвон"),
        ("Звонки", "/dashboard/calls", "Звонки"),
        ("Рабочее время", "/dashboard/work", "Рабочее время"),
    )
    for menu_name, path, content_heading in sections:
        deployment_page.open_section(
            menu_name=menu_name,
            expected_url=f"{test_settings.web_base_url}{path}",
            content_heading=content_heading,
        )

    work_url = f"{test_settings.web_base_url}/dashboard/work"
    deployment_page.reload(
        work_url,
        content_heading="Рабочее время",
    )
    deployment_page.open_section(
        menu_name="Рабочий стол",
        expected_url=home_url,
        content_heading="Последние звонки",
    )

    deployment_page.assert_no_loading_errors()
