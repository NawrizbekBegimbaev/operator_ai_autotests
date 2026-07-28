from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.direct_url_access_page import DirectUrlAccessPage


AuthorizedPageFactory = Callable[[str], Page]


@dataclass(frozen=True)
class CrossRoleDirectUrlCase:
    case_id: str
    role: str
    route_paths: tuple[str, ...]


def _cross_role_param(
    *,
    case_id: str,
    role: str,
    role_label: str,
    route_paths: tuple[str, ...],
    redirect_path: str,
) -> object:
    return pytest.param(
        CrossRoleDirectUrlCase(
            case_id=case_id,
            role=role,
            route_paths=route_paths,
        ),
        marks=pytest.mark.xfail(
            reason=(
                f"BUG-021: вместо заглушек доступа {role_label} "
                f"перенаправляется на {redirect_path}"
            ),
            strict=True,
        ),
        id=case_id,
    )


CROSS_ROLE_DIRECT_URL_CASES = (
    _cross_role_param(
        case_id="TC-027",
        role="rop",
        role_label="РОП",
        route_paths=(
            "/dashboard/calling",
            "/dashboard/work",
            "/dashboard/home",
        ),
        redirect_path="/dashboard/dynamic-form",
    ),
    _cross_role_param(
        case_id="TC-028",
        role="superadmin",
        role_label="супер-админ",
        route_paths=(
            "/dashboard/dynamic-form",
            "/dashboard/mezonlar",
            "/dashboard/operator-pipelines",
            "/dashboard/attendance",
        ),
        redirect_path="/dashboard/rop",
    ),
    _cross_role_param(
        case_id="TC-029",
        role="superadmin",
        role_label="супер-админ",
        route_paths=(
            "/dashboard/calling",
            "/dashboard/calls",
            "/dashboard/work",
            "/dashboard/home",
        ),
        redirect_path="/dashboard/rop",
    ),
)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.auth
@pytest.mark.parametrize("access_case", CROSS_ROLE_DIRECT_URL_CASES)
def test_cross_role_direct_urls_show_forbidden_without_data_leak(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    access_case: CrossRoleDirectUrlCase,
) -> None:
    """
    TC-027: РОП не открывает рабочие экраны оператора.
    TC-028: супер-админ не открывает экраны РОП.
    TC-029: супер-админ не открывает рабочие экраны оператора.
    """
    checked_routes: list[tuple[str, Page, DirectUrlAccessPage]] = []

    for route_path in access_case.route_paths:
        page = authorized_page_factory(access_case.role)
        direct_access_page = DirectUrlAccessPage(page)
        direct_access_page.open_protected_route(
            test_settings.web_base_url,
            route_path,
        )

        for description, protected_locator in (
            direct_access_page.protected_content[route_path].items()
        ):
            expect(
                protected_locator,
                f"[{access_case.case_id}] при прямом переходе на "
                f"{route_path} защищённый {description} не должен "
                "появляться даже кратковременно",
            ).to_have_count(0)

        observed_dom_markers = direct_access_page.observed_dom_markers()
        assert observed_dom_markers == [], (
            f"[{access_case.case_id}] при прямом переходе на "
            f"{route_path} в DOM кратковременно появились защищённые "
            f"данные: {observed_dom_markers}"
        )

        if route_path == "/dashboard/calling":
            calling_requests = [
                request_path
                for request_path in direct_access_page.protected_requests
                if (
                    request_path
                    in DirectUrlAccessPage.CALLING_CAPTURE_ENDPOINTS
                )
            ]
            assert calling_requests == [], (
                f"[{access_case.case_id}] при прямом переходе на "
                "/dashboard/calling не должны вызываться "
                "/v1/calling/queue и /v1/calling/next: лид не должен "
                f"быть захвачен; получены запросы: {calling_requests}"
            )

        assert direct_access_page.protected_requests == [], (
            f"[{access_case.case_id}] при прямом переходе на "
            f"{route_path} ожидали отсутствие запросов защищённого API, "
            f"получили: {direct_access_page.protected_requests}"
        )
        assert direct_access_page.protected_responses == [], (
            f"[{access_case.case_id}] при прямом переходе на "
            f"{route_path} ожидали отсутствие ответов защищённого API, "
            f"получили: {direct_access_page.protected_responses}"
        )

        checked_routes.append((route_path, page, direct_access_page))

    for route_path, page, direct_access_page in checked_routes:
        expect(
            page,
            f"[{access_case.case_id}] после прямого перехода на "
            f"{route_path} ожидали сохранение точного адреса заглушки",
        ).to_have_url(f"{test_settings.web_base_url}{route_path}")
        expect(
            direct_access_page.forbidden_heading,
            f"[{access_case.case_id}] на {route_path} ожидали "
            "точный заголовок заглушки доступа",
        ).to_have_text("Permission denied")
