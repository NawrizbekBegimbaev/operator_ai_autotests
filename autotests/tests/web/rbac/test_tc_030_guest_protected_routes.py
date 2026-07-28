from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.guest_protected_access_page import (
    GuestProtectedAccessPage,
)
from autotests.pages.login_page import LoginPage


PROTECTED_ROUTES = (
    "/dashboard/calls",
    "/dashboard/rop",
    "/dashboard/mezonlar",
)


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.auth
def test_tc_030_guest_is_redirected_without_protected_data(
    clean_login_page: Page,
    test_settings: Settings,
) -> None:
    """
    TC-030 — незалогиненный гость не открывает внутренние разделы.

    Ожидаемый результат: /dashboard/calls, /dashboard/rop и
    /dashboard/mezonlar приводят на страницу входа; защищённый DOM не
    появляется даже кратковременно.
    """
    login_page = LoginPage(clean_login_page)
    protected_access = GuestProtectedAccessPage(clean_login_page)
    expected_sign_in = urlsplit(
        f"{test_settings.web_base_url}{LoginPage.SIGN_IN_PATH}"
    )

    for route_path in PROTECTED_ROUTES:
        protected_access.open_protected_route(
            test_settings.web_base_url,
            route_path,
        )

        expect(
            login_page.username_input,
            f"[TC-030] после гостевого перехода на {route_path} "
            "ожидали видимую форму входа",
        ).to_be_visible()
        actual_url = urlsplit(clean_login_page.url)
        assert (
            actual_url.scheme,
            actual_url.netloc,
            actual_url.path,
        ) == (
            expected_sign_in.scheme,
            expected_sign_in.netloc,
            expected_sign_in.path,
        ), (
            f"[TC-030] после гостевого перехода на {route_path} ожидали "
            f"страницу {test_settings.web_base_url}{LoginPage.SIGN_IN_PATH}, "
            f"получили {clean_login_page.url}"
        )

        for description, protected_locator in (
            protected_access.protected_content[route_path].items()
        ):
            expect(
                protected_locator,
                f"[TC-030] на {route_path} защищённый {description} "
                "не должен присутствовать",
            ).to_have_count(0)

        observed_markers = protected_access.observed_dom_markers()
        assert observed_markers == [], (
            f"[TC-030] при гостевом переходе на {route_path} защищённый "
            f"DOM кратковременно появился: {observed_markers}"
        )
