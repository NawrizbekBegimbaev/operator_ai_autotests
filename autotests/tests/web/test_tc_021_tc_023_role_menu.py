from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.dashboard_navigation import DashboardNavigation


AuthorizedPageFactory = Callable[[str], Page]


ALL_ROLE_MENU_NAMES = (
    "РОПы",
    "Лиды",
    "Тарифы",
    "Правила",
    "Операторы",
    "Настройка очереди",
    "Критерии",
    "Посещаемость",
    "Рабочий стол",
    "Режим звонков",
    "Звонки",
    "Рабочее время",
)


@dataclass(frozen=True)
class RoleMenuCase:
    case_id: str
    role: str
    expected_path: str
    allowed_menu_names: tuple[str, ...]

    @property
    def forbidden_menu_names(self) -> tuple[str, ...]:
        return tuple(
            name
            for name in ALL_ROLE_MENU_NAMES
            if name not in self.allowed_menu_names
        )


ROLE_MENU_CASES = (
    pytest.param(
        RoleMenuCase(
            case_id="TC-021",
            role="superadmin",
            expected_path="/dashboard/rop",
            allowed_menu_names=("РОПы", "Лиды", "Тарифы"),
        ),
        id="TC-021",
    ),
    pytest.param(
        RoleMenuCase(
            case_id="TC-022",
            role="rop",
            expected_path="/dashboard/dynamic-form",
            allowed_menu_names=(
                "Правила",
                "Операторы",
                "Настройка очереди",
                "Критерии",
                "Посещаемость",
            ),
        ),
        id="TC-022",
    ),
    pytest.param(
        RoleMenuCase(
            case_id="TC-023",
            role="operator",
            expected_path="/dashboard/home",
            allowed_menu_names=(
                "Рабочий стол",
                "Режим звонков",
                "Звонки",
                "Рабочее время",
            ),
        ),
        id="TC-023",
    ),
)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.rbac
@pytest.mark.auth
@pytest.mark.parametrize("menu_case", ROLE_MENU_CASES)
def test_role_menu_contains_only_allowed_sections(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    menu_case: RoleMenuCase,
) -> None:
    """
    TC-021: супер-админ видит только «РОПы», «Лиды», «Тарифы».
    TC-022: РОП видит только пять управленческих разделов.
    TC-023: оператор видит только четыре рабочих раздела.
    """
    page: Page = authorized_page_factory(menu_case.role)
    navigation = DashboardNavigation(page, ALL_ROLE_MENU_NAMES)

    navigation.open_start_page(test_settings.web_base_url)

    expect(
        page,
        f"[{menu_case.case_id}] для роли {menu_case.role!r} ожидали "
        f"точный стартовый адрес {menu_case.expected_path}",
    ).to_have_url(
        f"{test_settings.web_base_url}{menu_case.expected_path}"
    )

    for menu_name in menu_case.allowed_menu_names:
        expect(
            navigation.links[menu_name],
            f"[{menu_case.case_id}] ожидали видимый разрешённый пункт "
            f"меню «{menu_name}»",
        ).to_be_visible()

    for menu_name in menu_case.forbidden_menu_names:
        expect(
            navigation.links[menu_name],
            f"[{menu_case.case_id}] запрещённый пункт меню "
            f"«{menu_name}» не должен присутствовать",
        ).to_have_count(0)
