from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage


@dataclass(frozen=True)
class InvalidCredentialsCase:
    case_id: str
    existing_username: bool


INVALID_CREDENTIALS_CASES = (
    pytest.param(
        InvalidCredentialsCase(case_id="TC-004", existing_username=True),
        marks=pytest.mark.critical,
        id="TC-004",
    ),
    pytest.param(
        InvalidCredentialsCase(case_id="TC-005", existing_username=False),
        marks=pytest.mark.high,
        id="TC-005",
    ),
)


@pytest.mark.web
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.auth
@pytest.mark.parametrize("case", INVALID_CREDENTIALS_CASES)
def test_invalid_credentials_rejected_without_account_disclosure(
    clean_login_page: Page,
    test_settings: Settings,
    case: InvalidCredentialsCase,
) -> None:
    """
    TC-004 — существующий логин с неверным паролем не пускает в систему.
    TC-005 — несуществующий логин не раскрывает наличие учётной записи.

    Ожидаемый результат обоих кейсов: вход не выполнен; пользователь остаётся
    на точном адресе /auth/jwt/sign-in; над формой показан красный alert с
    одинаковым универсальным сообщением «login yoki parol noto'g'ri»;
    пароль остаётся скрытым.
    """
    login_page = LoginPage(clean_login_page)
    case_prefix = f"[{case.case_id}]"
    username = (
        test_settings.superadmin_username
        if case.existing_username
        else f"AT-{uuid4().hex[:8]}"
    )
    password = (
        f"{test_settings.superadmin_password}x"
        if case.existing_username
        else f"AT-{uuid4().hex}"
    )

    login_page.open(test_settings.web_base_url)
    login_page.sign_in(username=username, password=password)

    expect(
        clean_login_page,
        f"{case_prefix} после неверных данных ожидали остаться на странице входа",
    ).to_have_url(f"{test_settings.web_base_url}/auth/jwt/sign-in")
    expect(
        login_page.error_alert,
        f"{case_prefix} ожидали видимую плашку ошибки над формой",
    ).to_be_visible()
    expect(
        login_page.error_alert,
        f"{case_prefix} ожидали одинаковое сообщение без раскрытия существования логина",
    ).to_have_text("login yoki parol noto'g'ri")
    expect(
        login_page.error_alert,
        f"{case_prefix} ожидали красную плашку severity=error",
    ).to_have_class(re.compile(r"\bMuiAlert-colorError\b"))
    expect(
        login_page.password_input,
        f"{case_prefix} после ошибки ожидали скрытое поле пароля",
    ).to_have_attribute("type", "password")
