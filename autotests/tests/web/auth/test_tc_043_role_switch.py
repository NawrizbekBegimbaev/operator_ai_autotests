from __future__ import annotations

import json
import re
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, Response, expect

from autotests.config import Credentials, Settings
from autotests.pages.account_menu import AccountMenu
from autotests.pages.dashboard_navigation import DashboardNavigation
from autotests.pages.direct_url_access_page import DirectUrlAccessPage
from autotests.pages.login_page import LoginPage
from autotests.support.login_rate_guard import LoginRateGuard


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
ROP_MENU_NAMES = (
    "Правила",
    "Операторы",
    "Настройка очереди",
    "Критерии",
    "Посещаемость",
)
OPERATOR_MENU_NAMES = (
    "Рабочий стол",
    "Режим звонков",
    "Звонки",
    "Рабочее время",
)


def _sign_in_and_require_role(
    page: Page,
    login_page: LoginPage,
    login_rate_guard: LoginRateGuard,
    credentials: Credentials,
    *,
    expected_role: str,
) -> dict[str, object]:
    login_rate_guard.before_attempt()
    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and urlsplit(response.url).path == "/v1/auth/login"
        )
    ) as login_response_info:
        login_page.sign_in(
            username=credentials.username,
            password=credentials.password,
        )

    login_response: Response = login_response_info.value
    assert login_response.status == 200, (
        f"[TC-043] для роли {expected_role!r} ожидали login 200, получили "
        f"{login_response.status}: {login_response.text()}"
    )
    body = login_response.json()
    assert isinstance(body, dict), (
        f"[TC-043] ожидали JSON-объект входа, получили {body!r}"
    )
    user = body.get("user")
    assert isinstance(user, dict), (
        f"[TC-043] ожидали объект user, получили {body!r}"
    )
    assert user.get("role") == expected_role, (
        f"[TC-043] ожидали role={expected_role!r}, получили {user!r}"
    )
    assert user.get("username") == credentials.username, (
        "[TC-043] API вернул другого пользователя: "
        f"ожидали {credentials.username!r}, получили {user!r}"
    )
    return user


def _assert_exact_menu(
    navigation: DashboardNavigation,
    *,
    expected_names: tuple[str, ...],
    checkpoint: str,
) -> None:
    for menu_name in expected_names:
        expect(
            navigation.links[menu_name],
            f"{checkpoint} ожидали пункт меню «{menu_name}»",
        ).to_be_visible()

    for menu_name in ALL_ROLE_MENU_NAMES:
        if menu_name in expected_names:
            continue
        expect(
            navigation.links[menu_name],
            f"{checkpoint} старый/чужой пункт «{menu_name}» не должен остаться",
        ).to_have_count(0)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.auth
@pytest.mark.serial
def test_tc_043_logout_then_operator_login_does_not_keep_rop_access(
    clean_login_page: Page,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> None:
    """TC-043 — после РОП новая сессия Оператора не наследует его права."""
    page = clean_login_page
    login_page = LoginPage(page)
    account_menu = AccountMenu(page)
    navigation = DashboardNavigation(page, ALL_ROLE_MENU_NAMES)
    rop_credentials = test_settings.credentials_for("rop")
    operator_credentials = test_settings.credentials_for("operator")

    login_page.open(test_settings.web_base_url)
    rop_user = _sign_in_and_require_role(
        page,
        login_page,
        login_rate_guard,
        rop_credentials,
        expected_role="rop",
    )
    expect(
        page,
        "[TC-043] после входа РОП ожидали его стартовый раздел",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/dynamic-form")
    _assert_exact_menu(
        navigation,
        expected_names=ROP_MENU_NAMES,
        checkpoint="[TC-043:ROP]",
    )

    navigation.links["Критерии"].click()
    expect(
        page,
        "[TC-043] РОП должен открывать собственный раздел «Критерии»",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/mezonlar")
    expect(
        page.get_by_role("heading", name="Критерии", exact=True),
    ).to_be_visible()

    account_menu.open()
    expect(account_menu.logout_button).to_be_visible()
    account_menu.logout()
    expect(
        page,
        "[TC-043] после выхода РОП ожидали страницу входа",
    ).to_have_url(
        re.compile(
            rf"^{re.escape(test_settings.web_base_url)}"
            rf"{re.escape(LoginPage.SIGN_IN_PATH)}(?:\?.*)?$"
        )
    )
    expect(login_page.username_input).to_be_visible()

    operator_user = _sign_in_and_require_role(
        page,
        login_page,
        login_rate_guard,
        operator_credentials,
        expected_role="operator",
    )
    expect(
        page,
        "[TC-043] после нового входа ожидали разрешённый раздел Оператора",
    ).to_have_url(
        re.compile(
            rf"^{re.escape(test_settings.web_base_url)}"
            r"/dashboard/(?:home|calls)$"
        )
    )
    _assert_exact_menu(
        navigation,
        expected_names=OPERATOR_MENU_NAMES,
        checkpoint="[TC-043:Operator]",
    )

    storage_user_raw = page.evaluate(
        "() => localStorage.getItem('jwt_user')"
    )
    assert isinstance(storage_user_raw, str) and storage_user_raw, (
        "[TC-043] после входа Оператора ожидали jwt_user в localStorage"
    )
    storage_user = json.loads(storage_user_raw)
    assert isinstance(storage_user, dict), (
        f"[TC-043] jwt_user должен быть объектом: {storage_user!r}"
    )
    assert storage_user.get("id") == operator_user.get("id"), (
        "[TC-043] browser storage содержит не текущего Оператора: "
        f"{storage_user!r}"
    )
    assert storage_user.get("role") == "operator", (
        f"[TC-043] в browser storage осталась старая роль: {storage_user!r}"
    )
    assert storage_user.get("id") != rop_user.get("id"), (
        "[TC-043] после нового входа в storage остался прежний РОП"
    )

    direct_access = DirectUrlAccessPage(page)
    direct_access.open_protected_route(
        test_settings.web_base_url,
        "/dashboard/mezonlar",
    )
    expect(
        direct_access.protected_content["/dashboard/mezonlar"][
            "заголовок критериев"
        ],
        "[TC-043] Оператор не должен видеть раздел «Критерии»",
    ).to_have_count(0)
    assert direct_access.observed_dom_markers() == [], (
        "[TC-043] после смены роли в DOM появились данные «Критериев»: "
        f"{direct_access.observed_dom_markers()!r}"
    )
    assert direct_access.protected_requests == [], (
        "[TC-043] после смены роли Оператор не должен вызывать API РОП: "
        f"{direct_access.protected_requests!r}"
    )
    _assert_exact_menu(
        navigation,
        expected_names=OPERATOR_MENU_NAMES,
        checkpoint="[TC-043:direct URL]",
    )
