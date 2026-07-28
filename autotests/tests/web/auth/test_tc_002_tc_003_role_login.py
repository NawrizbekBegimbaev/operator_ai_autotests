from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import pytest
from playwright.sync_api import Locator, Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage
from autotests.pages.operator_calls_page import OperatorCallsPage
from autotests.pages.rop_rules_page import RopRulesPage


class TargetPage(Protocol):
    main_content: Locator
    menu_links: dict[str, Locator]


@dataclass(frozen=True)
class RoleLoginCase:
    case_id: str
    role: str
    expected_path: str
    page_factory: Callable[[Page], TargetPage]
    content_description: str


ROLE_LOGIN_CASES = (
    RoleLoginCase(
        case_id="TC-002",
        role="rop",
        expected_path="/dashboard/dynamic-form",
        page_factory=RopRulesPage,
        content_description="раздел «Правила» с заголовком «Статусы лида»",
    ),
    RoleLoginCase(
        case_id="TC-003",
        role="operator",
        expected_path="/dashboard/calls",
        page_factory=OperatorCallsPage,
        content_description="таблицу лидов в разделе «Звонки»",
    ),
)


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.auth
@pytest.mark.parametrize(
    "login_case",
    ROLE_LOGIN_CASES,
    ids=["TC-002", "TC-003"],
)
def test_role_login_lands_on_expected_page(
    clean_login_page: Page,
    test_settings: Settings,
    login_case: RoleLoginCase,
) -> None:
    credentials = test_settings.credentials_for(login_case.role)
    login_page = LoginPage(clean_login_page)
    target_page = login_case.page_factory(clean_login_page)

    login_page.open(test_settings.web_base_url)
    login_page.sign_in(
        username=credentials.username,
        password=credentials.password,
    )

    expect(
        clean_login_page,
        f"[{login_case.case_id}] после входа ожидали точный адрес "
        f"{login_case.expected_path}",
    ).to_have_url(
        f"{test_settings.web_base_url}{login_case.expected_path}"
    )
    expect(
        target_page.main_content,
        f"[{login_case.case_id}] ожидали видимый {login_case.content_description}",
    ).to_be_visible()

    for menu_name, menu_link in target_page.menu_links.items():
        expect(
            menu_link,
            f"[{login_case.case_id}] ожидали видимый пункт меню «{menu_name}»",
        ).to_be_visible()
