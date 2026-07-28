from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.direct_url_access_page import DirectUrlAccessPage


AuthorizedPageFactory = Callable[[str], Page]


@dataclass(frozen=True)
class DirectRouteExpectation:
    route_path: str
    expected_path: str
    expects_forbidden_view: bool


@dataclass(frozen=True)
class DirectUrlAccessCase:
    case_id: str
    role: str
    routes: tuple[DirectRouteExpectation, ...]


DIRECT_URL_ACCESS_CASES = (
    pytest.param(
        DirectUrlAccessCase(
            case_id="TC-024",
            role="operator",
            routes=(
                DirectRouteExpectation(
                    route_path="/dashboard/rop",
                    expected_path="/dashboard/calls",
                    expects_forbidden_view=False,
                ),
            ),
        ),
        id="TC-024",
    ),
    pytest.param(
        DirectUrlAccessCase(
            case_id="TC-025",
            role="operator",
            routes=(
                DirectRouteExpectation(
                    route_path="/dashboard/plans",
                    expected_path="/dashboard/plans",
                    expects_forbidden_view=True,
                ),
                DirectRouteExpectation(
                    route_path="/dashboard/leads",
                    expected_path="/dashboard/leads",
                    expects_forbidden_view=True,
                ),
            ),
        ),
        marks=pytest.mark.xfail(
            reason=(
                "BUG-020: вместо заглушки доступа оператор перенаправляется "
                "на /dashboard/calls"
            ),
            strict=True,
        ),
        id="TC-025",
    ),
    pytest.param(
        DirectUrlAccessCase(
            case_id="TC-026",
            role="rop",
            routes=(
                DirectRouteExpectation(
                    route_path="/dashboard/rop",
                    expected_path="/dashboard/rop",
                    expects_forbidden_view=True,
                ),
                DirectRouteExpectation(
                    route_path="/dashboard/leads",
                    expected_path="/dashboard/leads",
                    expects_forbidden_view=True,
                ),
                DirectRouteExpectation(
                    route_path="/dashboard/plans",
                    expected_path="/dashboard/plans",
                    expects_forbidden_view=True,
                ),
            ),
        ),
        marks=pytest.mark.xfail(
            reason=(
                "BUG-020: вместо заглушки доступа РОП перенаправляется "
                "на /dashboard/dynamic-form"
            ),
            strict=True,
        ),
        id="TC-026",
    ),
)


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.parametrize("access_case", DIRECT_URL_ACCESS_CASES)
def test_direct_url_does_not_expose_forbidden_sections(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    access_case: DirectUrlAccessCase,
) -> None:
    """
    TC-024: оператор с /dashboard/rop перенаправляется на /dashboard/calls.
    TC-025: оператор видит точную заглушку на /dashboard/plans и /dashboard/leads.
    TC-026: РОП видит точную заглушку на трёх разделах супер-админа.
    """
    page = authorized_page_factory(access_case.role)
    direct_access_page = DirectUrlAccessPage(page)

    for route in access_case.routes:
        direct_access_page.open_protected_route(
            test_settings.web_base_url,
            route.route_path,
        )

        for description, protected_locator in (
            direct_access_page.protected_content[route.route_path].items()
        ):
            expect(
                protected_locator,
                f"[{access_case.case_id}] при прямом переходе на "
                f"{route.route_path} защищённый {description} не должен "
                "появляться даже кратковременно",
            ).to_have_count(0)

        observed_dom_markers = direct_access_page.observed_dom_markers()
        assert observed_dom_markers == [], (
            f"[{access_case.case_id}] при прямом переходе на "
            f"{route.route_path} в DOM кратковременно появились защищённые "
            f"данные: {observed_dom_markers}"
        )
        assert direct_access_page.protected_responses == [], (
            f"[{access_case.case_id}] при прямом переходе на "
            f"{route.route_path} ожидали отсутствие ответов защищённого API, "
            f"получили: {direct_access_page.protected_responses}"
        )

        expect(
            page,
            f"[{access_case.case_id}] после прямого перехода на "
            f"{route.route_path} ожидали точный адрес {route.expected_path}",
        ).to_have_url(
            f"{test_settings.web_base_url}{route.expected_path}"
        )

        if route.expects_forbidden_view:
            expect(
                direct_access_page.forbidden_heading,
                f"[{access_case.case_id}] на {route.route_path} ожидали "
                "точный заголовок заглушки доступа",
            ).to_have_text("Permission denied")
        else:
            expect(
                direct_access_page.forbidden_heading,
                f"[{access_case.case_id}] после разрешённого редиректа "
                "заглушка доступа не должна отображаться",
            ).to_have_count(0)
