from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

import pytest
from playwright.sync_api import Page, Playwright, expect

from autotests.config import Settings
from autotests.pages.account_change_password_dialog import (
    AccountChangePasswordDialog,
)
from autotests.pages.account_menu import AccountMenu
from autotests.pages.login_page import LoginPage
from autotests.support.auth_requests import login, require_access_token
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.temporary_users import TemporaryOperator


AuthorizedPageFactory = Callable[[str], Page]


def _open_password_dialog(page: Page) -> AccountChangePasswordDialog:
    account_menu = AccountMenu(page)
    dialog = AccountChangePasswordDialog(page)
    account_menu.open()
    expect(
        account_menu.change_password_button,
        "[password-dialog] ожидали кнопку «Сменить пароль»",
    ).to_be_visible()
    account_menu.open_change_password()
    expect(
        dialog.dialog,
        "[password-dialog] ожидали открытый диалог смены пароля",
    ).to_be_visible()
    return dialog


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.negative
@pytest.mark.validation
@pytest.mark.auth
def test_tc_016_password_confirmation_mismatch_blocks_submit(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """TC-016 — несовпадающий повтор нового пароля нельзя отправить."""
    credentials = test_settings.credentials_for("operator")
    page = authorized_page_factory("operator")
    page.goto(
        f"{test_settings.web_base_url}/dashboard/home",
        wait_until="commit",
    )
    dialog = _open_password_dialog(page)

    dialog.fill(
        old_password=credentials.password,
        new_password="password123",
        confirmation="password124",
    )

    expect(
        dialog.password_mismatch,
        "[TC-016] ожидали точную подсказку о несовпадении паролей",
    ).to_be_visible()
    expect(
        dialog.save_button,
        "[TC-016] при несовпадающих паролях кнопка сохранения должна быть неактивна",
    ).to_be_disabled()


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.boundary
@pytest.mark.validation
@pytest.mark.auth
@pytest.mark.serial
def test_tc_017_new_password_boundary_seven_rejected_eight_accepted(
    clean_login_page: Page,
    playwright: Playwright,
    api_base_url: str,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
    temporary_operator: TemporaryOperator,
) -> None:
    """TC-017 — 7 символов отклоняются, пароль из 8 символов сохраняется."""
    login_page = LoginPage(clean_login_page)
    login_page.open(test_settings.web_base_url)
    login_rate_guard.before_attempt()
    login_page.sign_in(
        username=temporary_operator.username,
        password=temporary_operator.password,
    )
    expect(
        clean_login_page,
        "[TC-017 setup] ожидали рабочий стол временного оператора",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/home")

    dialog = _open_password_dialog(clean_login_page)
    dialog.fill(
        old_password=temporary_operator.password,
        new_password="1234567",
        confirmation="1234567",
    )

    expect(
        dialog.password_too_short,
        "[TC-017] для 7 символов ожидали точную подсказку минимальной длины",
    ).to_be_visible()
    expect(
        dialog.save_button,
        "[TC-017] пароль из 7 символов нельзя сохранять",
    ).to_be_disabled()

    accepted_password = f"A7!{uuid4().hex[:5]}"
    assert len(accepted_password) == 8
    dialog.new_password_input.fill(accepted_password)
    dialog.confirm_password_input.fill(accepted_password)
    expect(
        dialog.password_too_short,
        "[TC-017] после ввода 8 символов подсказка должна исчезнуть",
    ).to_have_count(0)
    expect(
        dialog.save_button,
        "[TC-017] пароль из 8 символов должен разрешать сохранение",
    ).to_be_enabled()
    dialog.save()

    expect(
        dialog.success_alert,
        "[TC-017] после сохранения ожидали уведомление «Parol yangilandi»",
    ).to_be_visible()
    expect(
        dialog.dialog,
        "[TC-017] после успешной смены пароля диалог должен закрыться",
    ).to_have_count(0)

    public_request = playwright.request.new_context(base_url=api_base_url)
    try:
        changed_login = login(
            public_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=accepted_password,
        )
        _, changed_user = require_access_token(
            changed_login,
            checkpoint="[TC-017] проверка входа с 8-символьным паролем",
        )
        assert changed_user.get("id") == temporary_operator.id, (
            "[TC-017] после смены пароля вошёл другой оператор: "
            f"{changed_user!r}"
        )
    finally:
        public_request.dispose()
