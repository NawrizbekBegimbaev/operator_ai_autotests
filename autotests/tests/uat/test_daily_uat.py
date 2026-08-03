from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import replace
from datetime import date
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.api.user_api import UserApi
from autotests.pages.account_menu import AccountMenu
from autotests.pages.deployment_smoke_page import DeploymentSmokePage
from autotests.pages.login_page import LoginPage
from autotests.pages.operator_list_page import OperatorListPage
from autotests.pages.rop_list_page import RopListPage
from autotests.support.auth_requests import login, require_access_token
from autotests.support.operator_work import operator_work_harness
from autotests.support.rop_api import cleanup_rops_by_username
from autotests.support.operator_api import cleanup_users_by_username, list_extensions
from autotests.uat.catalog import UATCase, load_catalog


Handler = Callable[[pytest.FixtureRequest], None]
CATALOG = load_catalog()


def _gate(case_id: str, reason: str) -> None:
    pytest.skip(f"UAT_GATE [{case_id}]: {reason}")


def _env_gate(case_id: str, names: tuple[str, ...], reason: str) -> None:
    missing = [name for name in names if not os.getenv(name, "").strip()]
    if missing:
        _gate(case_id, f"{reason}; не заданы {', '.join(missing)}")


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _uat_sys_001(request: pytest.FixtureRequest) -> None:
    playwright = request.getfixturevalue("playwright")
    api_base_url = request.getfixturevalue("api_base_url")
    api = playwright.request.new_context(base_url=api_base_url)
    try:
        health = api.get("/healthz")
        ready = api.get("/readyz")
        plans = api.get("/v1/plans")
        health_after = api.get("/healthz")
        ready_after = api.get("/readyz")
        health_status = health.status
        health_body = health.json()
        ready_status = ready.status
        ready_body = ready.json()
        plans_status = plans.status
        plans_body = plans.json()
        health_after_status = health_after.status
        health_after_body = health_after.json()
        ready_after_status = ready_after.status
        ready_after_body = ready_after.json()
    finally:
        api.dispose()
    assert health_status == 200 and health_body.get("status") == "ok", (
        "Backend не подтвердил состояние ok."
    )
    assert ready_status == 200 and ready_body.get("status") == "ready", (
        "Backend не подтвердил готовность к работе."
    )
    assert plans_status == 200, "Список тарифов недоступен пользователю."
    items = plans_body.get("items")
    assert isinstance(items, list) and items, "Список тарифов пуст."
    assert health_after_status == 200 and health_after_body.get("status") == "ok"
    assert ready_after_status == 200 and ready_after_body.get("status") == "ready"


def _uat_sys_002(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("clean_login_page")
    settings: Settings = request.getfixturevalue("test_settings")
    smoke = DeploymentSmokePage(page)
    login_page = LoginPage(page)
    login_page.open(settings.web_base_url)
    smoke.wait_for_resources(timeout_ms=15_000)
    expect(login_page.username_input).to_be_visible(timeout=15_000)
    expect(login_page.password_input).to_be_visible(timeout=15_000)
    expect(login_page.submit_button).to_be_enabled(timeout=15_000)
    smoke.assert_no_loading_errors()


def _select_language(page: Page, label: str) -> None:
    page.get_by_role("button", name="Til", exact=True).click()
    option = page.get_by_role("menuitem", name=label, exact=True)
    expect(option).to_be_visible()
    option.click()


def _uat_com_001(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("rop")
    settings: Settings = request.getfixturevalue("test_settings")
    page.goto(
        f"{settings.web_base_url}/dashboard/operators",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_role("progressbar")).to_have_count(0, timeout=20_000)
    expect(
        page.get_by_role("heading", name=re.compile(r"^Операторы"))
    ).to_be_visible(timeout=15_000)
    _select_language(page, "O'zbekcha")
    expect(
        page.get_by_role("heading", name=re.compile(r"^Operatorlar"))
    ).to_be_visible(timeout=15_000)
    _select_language(page, "Русский")
    expect(
        page.get_by_role("heading", name=re.compile(r"^Операторы"))
    ).to_be_visible(timeout=15_000)
    page.reload(wait_until="domcontentloaded")
    expect(page.get_by_role("progressbar")).to_have_count(0, timeout=20_000)
    expect(page.get_by_role("button", name="Til", exact=True)).to_have_text("ru")


def _uat_com_002(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("clean_login_page")
    settings: Settings = request.getfixturevalue("test_settings")
    temporary_operator = request.getfixturevalue("temporary_operator")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    playwright = request.getfixturevalue("playwright")
    new_password = f"UAT!{uuid4().hex[:12]}"
    login_page = LoginPage(page)
    login_page.open(settings.web_base_url)
    login_rate_guard.before_attempt()
    login_page.sign_in(temporary_operator.username, temporary_operator.password)
    expect(page).to_have_url(re.compile(r"/dashboard/(?:home|calls)$"))
    account = AccountMenu(page)
    account.open()
    change_button = page.get_by_role(
        "button",
        name=re.compile(r"^(?:Сменить пароль|Parolni o'zgartirish)$"),
    )
    expect(change_button).to_be_visible()
    change_button.click()
    dialog = page.get_by_role(
        "dialog",
        name=re.compile(r"^(?:Сменить пароль|Parolni o'zgartirish)$"),
    )
    expect(dialog).to_be_visible()
    old_input = dialog.get_by_label(re.compile(r"^(?:Текущий пароль|Eski parol)$"))
    new_input = dialog.get_by_label(re.compile(r"^(?:Новый пароль|Yangi parol)$"))
    confirm_input = dialog.get_by_label(
        re.compile(r"^(?:Повторите новый пароль|Yangi parolni takrorlang)$")
    )
    old_input.fill(temporary_operator.password)
    new_input.fill(new_password)
    confirm_input.fill(new_password)
    dialog.get_by_role(
        "button", name=re.compile(r"^(?:Сохранить|Saqlash)$")
    ).click()
    expect(page.get_by_role("alert")).to_contain_text(
        re.compile(r"(?:Пароль изменён|Parol yangilandi)", re.IGNORECASE)
    )
    account.open()
    page.get_by_role(
        "button", name=re.compile(r"^(?:Выйти|Chiqish)$")
    ).click()
    expect(login_page.username_input).to_be_visible()
    login_rate_guard.before_attempt()
    login_page.sign_in(temporary_operator.username, new_password)
    expect(page).to_have_url(re.compile(r"/dashboard/(?:home|calls)$"))

    public_api = playwright.request.new_context(base_url=settings.require_api_base_url())
    try:
        changed_login = login(
            public_api,
            login_rate_guard,
            username=temporary_operator.username,
            password=new_password,
        )
        token, _ = require_access_token(
            changed_login,
            checkpoint="[UAT-COM-002] вход для восстановления пароля",
        )
        restored = public_api.post(
            "/v1/auth/change-password",
            data={"old_password": new_password, "new_password": temporary_operator.password},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert restored.status == 200, "Не удалось восстановить пароль тестовой учётки."
    finally:
        public_api.dispose()


def _uat_lnd_001(request: pytest.FixtureRequest) -> None:
    _env_gate(
        "UAT-LND-001",
        ("OPERATOR_AI_LANDING_BASE_URL",),
        "нужен URL staging Landing",
    )
    page: Page = request.getfixturevalue("page")
    landing_url = os.environ["OPERATOR_AI_LANDING_BASE_URL"].rstrip("/")
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(landing_url, wait_until="networkidle")
    expect(page.get_by_role("heading", level=1)).to_be_visible()
    for section_id in ("muammo", "qanday-ishlaydi", "imkoniyatlar", "tariflar", "demo"):
        expect(page.locator(f"#{section_id}")).to_be_attached()
    expect(page.locator("#tariflar article").first).to_be_visible()
    assert not errors, "Landing открылся с runtime-ошибкой."


def _open_role_sections(
    request: pytest.FixtureRequest,
    *,
    role: str,
    start_path: str,
    sections: tuple[tuple[str, str], ...],
) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")(role)
    settings: Settings = request.getfixturevalue("test_settings")
    page.goto(
        f"{settings.web_base_url}{start_path}",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_role("progressbar")).to_have_count(0, timeout=20_000)
    for menu_name, path in sections:
        link = page.get_by_role("link", name=menu_name, exact=True)
        expect(link).to_be_visible(timeout=15_000)
        link.click()
        expect(page).to_have_url(f"{settings.web_base_url}{path}", timeout=15_000)
        expect(page.get_by_role("progressbar")).to_have_count(0, timeout=20_000)
        expect(page.get_by_text("Unexpected Application Error!", exact=True)).to_have_count(0)
    AccountMenu(page).open()
    logout = page.get_by_role("button", name="Выйти", exact=True)
    expect(logout).to_be_visible()
    logout.click()
    expect(LoginPage(page).username_input).to_be_visible()


def _uat_sa_001(request: pytest.FixtureRequest) -> None:
    _open_role_sections(
        request,
        role="superadmin",
        start_path="/dashboard/rop",
        sections=(("РОПы", "/dashboard/rop"), ("Лиды", "/dashboard/leads"), ("Тарифы", "/dashboard/plans")),
    )


def _uat_sa_002(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("superadmin")
    settings: Settings = request.getfixturevalue("test_settings")
    playwright = request.getfixturevalue("playwright")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    unique = uuid4().hex
    username = f"UAT-ROP-{unique[:8]}"
    password = f"UAT!{unique[:12]}"
    original_company = f"UAT Company {unique[:8]}"
    updated_company = f"UAT Updated {unique[:8]}"
    first_name = f"UAT{unique[:5]}"
    last_name = f"ROP{unique[5:10]}"
    phone = f"+99893{uuid4().int % 10_000_000:07d}"
    rop_list = RopListPage(page)
    superadmin_api = UserApi.from_authorized_page(
        page,
        settings.web_base_url,
        discovery_path=RopListPage.PATH,
    )
    created_id = ""
    operator_id = ""
    rop_request = None
    try:
        dialog = rop_list.open_create_dialog()
        dialog.fill(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            username=username,
            company_name=original_company,
        )
        dialog.select_tariff("Аналитика")
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path == "/v1/rops"
        ) as created_info:
            dialog.create()
        created_response = created_info.value
        assert created_response.status == 200, "Super-admin не смог создать ROP."
        created_body = created_response.json()
        created_id = str(created_body.get("id") or "")
        assert created_id and created_body.get("username") == username
        expect(rop_list.row_by_company(original_company)).to_have_count(1)

        edit = rop_list.open_edit_dialog(original_company)
        edit.fill(
            first_name=f"{first_name}X",
            last_name=f"{last_name}X",
            phone_subscriber=phone.removeprefix("+998"),
            company_name=updated_company,
        )
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as edited_info:
            edit.save_button.click()
        assert edited_info.value.status == 200, "Super-admin не смог изменить ROP."
        expect(rop_list.row_by_company(updated_company)).to_have_count(1)

        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as deactivated_info:
            rop_list.toggle_active(updated_company)
        assert deactivated_info.value.status == 200
        expect(rop_list.row_by_company(updated_company)).to_contain_text("Неактивен")
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as activated_info:
            rop_list.toggle_active(updated_company)
        assert activated_info.value.status == 200
        expect(rop_list.row_by_company(updated_company)).to_contain_text("Активен")

        public = playwright.request.new_context(base_url=settings.require_api_base_url())
        try:
            login_rate_guard.before_attempt()
            rop_login = login(
                public,
                login_rate_guard,
                username=username,
                password=password,
            )
            rop_token, _ = require_access_token(
                rop_login,
                checkpoint="[UAT-SA-002] вход созданного ROP",
            )
        finally:
            public.dispose()
        rop_request = playwright.request.new_context(
            base_url=settings.require_api_base_url(),
            extra_http_headers={
                "Authorization": f"Bearer {rop_token}",
                "Content-Type": "application/json",
            },
        )
        operator_unique = uuid4().hex
        operator_name = f"UAT Operator{operator_unique[:6]}"
        operator_response = rop_request.post(
            "/v1/operators",
            data={
                "username": f"UAT-OP-{operator_unique[:8]}",
                "password": f"UAT!{operator_unique[:12]}",
                "first_name": "UAT",
                "last_name": f"Operator{operator_unique[:6]}",
                "phone": f"+99890{uuid4().int % 10_000_000:07d}",
                "pbx_extension": f"UAT{operator_unique[:6]}",
                "salary": 1,
                "salary_day": date.today().isoformat(),
            },
        )
        assert operator_response.status == 200, (
            "Созданный ROP не смог создать временного Operator: "
            f"HTTP {operator_response.status}."
        )
        operator_body = operator_response.json()
        operator_id = str(operator_body.get("id") or "")
        assert operator_id
        page.goto(
            f"{settings.web_base_url}/dashboard/rop/{created_id}/operators",
            wait_until="commit",
        )
        expect(page.get_by_text(operator_name, exact=False)).to_be_visible()

        delete_operator = rop_request.delete(f"/v1/users/{operator_id}")
        assert delete_operator.status == 200
        operator_id = ""
        page.goto(f"{settings.web_base_url}{RopListPage.PATH}", wait_until="commit")
        delete_dialog = rop_list.open_delete_dialog(updated_company)
        with page.expect_response(
            lambda response: response.request.method == "DELETE"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as deleted_info:
            delete_dialog.confirm()
        assert deleted_info.value.status == 200
        expect(rop_list.row_by_company(updated_company)).to_have_count(0)
        created_id = ""
    finally:
        if rop_request is not None:
            if operator_id:
                rop_request.delete(f"/v1/users/{operator_id}")
            rop_request.dispose()
        if created_id:
            cleanup_rops_by_username(
                superadmin_api,
                username,
                checkpoint="[UAT-SA-002 cleanup]",
            )


def _uat_rop_001(request: pytest.FixtureRequest) -> None:
    _open_role_sections(
        request,
        role="rop",
        start_path="/dashboard/dynamic-form",
        sections=(
            ("Правила", "/dashboard/dynamic-form"),
            ("Операторы", "/dashboard/operators"),
            ("Настройка очереди", "/dashboard/operator-pipelines"),
            ("Критерии", "/dashboard/mezonlar"),
            ("Не пришли", "/dashboard/not-arrived"),
            ("Посещаемость", "/dashboard/attendance"),
        ),
    )


def _uat_rop_002(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("rop")
    settings: Settings = request.getfixturevalue("test_settings")
    playwright = request.getfixturevalue("playwright")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    rop_request = request.getfixturevalue("rop_api_request")
    original_draft = request.getfixturevalue("operator_draft")
    try:
        extensions = list_extensions(
            rop_request,
            checkpoint="[UAT-ROP-002 setup]",
        )
    except (AssertionError, RuntimeError) as error:
        _gate("UAT-ROP-002", f"нет доступного OnlinePBX extension: {error}")
    free = [
        item
        for item in extensions
        if item.get("enabled") is True and item.get("assigned") is False
    ]
    if not free:
        _gate("UAT-ROP-002", "на staging нет свободного OnlinePBX extension")
    extension = str(free[0].get("extension") or "")
    if not extension:
        _gate("UAT-ROP-002", "свободный OnlinePBX extension не содержит номер")
    draft = replace(original_draft, pbx_extension=extension, salary=1_000_000)
    operator_list = OperatorListPage(page)
    operator_list.open(settings.web_base_url)
    created_id = ""
    current_first_name = draft.first_name
    current_last_name = draft.last_name
    try:
        dialog = operator_list.open_create_dialog()
        dialog.fill_personal_data(draft)
        dialog.select_extension(extension)
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path == "/v1/operators"
        ) as created_info:
            dialog.create()
        created_response = created_info.value
        assert created_response.status == 200, "ROP не смог создать Operator."
        created = created_response.json()
        created_id = str(created.get("id") or "")
        assert created_id and created.get("pbx_extension") == extension
        expect(
            operator_list.row_by_full_name(current_first_name, current_last_name)
        ).to_have_count(1)

        public = playwright.request.new_context(base_url=settings.require_api_base_url())
        try:
            login_rate_guard.before_attempt()
            initial_login = login(
                public,
                login_rate_guard,
                username=draft.username,
                password=draft.password,
            )
            _, initial_user = require_access_token(
                initial_login,
                checkpoint="[UAT-ROP-002] вход нового Operator",
            )
            assert initial_user.get("id") == created_id
        finally:
            public.dispose()

        edit = operator_list.open_edit_dialog(current_first_name, current_last_name)
        current_first_name = f"{draft.first_name}X"
        current_last_name = f"{draft.last_name}X"
        edit.first_name_input.fill(current_first_name)
        edit.last_name_input.fill(current_last_name)
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as edited_info:
            edit.save_button.click()
        assert edited_info.value.status == 200
        expect(
            operator_list.row_by_full_name(current_first_name, current_last_name)
        ).to_have_count(1)

        row = operator_list.row_by_full_name(current_first_name, current_last_name)
        row.get_by_role("button").nth(1).click()
        reset_dialog = page.get_by_role("dialog", name="Сброс пароля", exact=True)
        expect(reset_dialog).to_be_visible()
        new_password = f"UAT-New!{uuid4().hex[:10]}"
        reset_dialog.get_by_label("Новый пароль", exact=True).fill(new_password)
        reset_dialog.get_by_label("Повторите новый пароль", exact=True).fill(new_password)
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path == f"/v1/users/{created_id}/password"
        ) as reset_info:
            reset_dialog.get_by_role("button", name="Сохранить", exact=True).click()
        assert reset_info.value.status == 200
        expect(page.get_by_role("alert")).to_contain_text("Пароль обновлён")

        public = playwright.request.new_context(base_url=settings.require_api_base_url())
        try:
            login_rate_guard.before_attempt()
            reset_login = login(
                public,
                login_rate_guard,
                username=draft.username,
                password=new_password,
            )
            _, reset_user = require_access_token(
                reset_login,
                checkpoint="[UAT-ROP-002] вход после reset",
            )
            assert reset_user.get("id") == created_id
        finally:
            public.dispose()

        row = operator_list.row_by_full_name(current_first_name, current_last_name)
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as deactivated_info:
            row.get_by_role("button").nth(2).click()
        assert deactivated_info.value.status == 200
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as activated_info:
            operator_list.row_by_full_name(
                current_first_name, current_last_name
            ).get_by_role("button").nth(2).click()
        assert activated_info.value.status == 200

        operator_list.row_by_full_name(current_first_name, current_last_name).click()
        expect(page).to_have_url(
            f"{settings.web_base_url}/dashboard/operators/{created_id}"
        )
        expect(page.get_by_text(f"{current_first_name} {current_last_name}", exact=True)).to_be_visible()
        expect(page.get_by_text(extension, exact=False).first).to_be_visible()

        operator_list.open(settings.web_base_url)
        row = operator_list.row_by_full_name(current_first_name, current_last_name)
        row.get_by_role("button").nth(3).click()
        delete_dialog = page.get_by_role(
            "dialog", name="Удалить пользователя", exact=True
        )
        expect(delete_dialog).to_be_visible()
        with page.expect_response(
            lambda response: response.request.method == "DELETE"
            and urlsplit(response.url).path == f"/v1/users/{created_id}"
        ) as deleted_info:
            delete_dialog.get_by_role("button", name="Удалить", exact=True).click()
        assert deleted_info.value.status == 200
        expect(operator_list.row_by_full_name(current_first_name, current_last_name)).to_have_count(0)
        created_id = ""
    finally:
        if created_id:
            cleanup_users_by_username(
                rop_request,
                draft.username,
                checkpoint="[UAT-ROP-002 cleanup]",
            )


def _uat_op_001(request: pytest.FixtureRequest) -> None:
    _open_role_sections(
        request,
        role="operator",
        start_path="/dashboard/calls",
        sections=(
            ("Рабочий стол", "/dashboard/home"),
            ("Режим звонков", "/dashboard/calling"),
            ("Звонки", "/dashboard/calls"),
            ("Рабочее время", "/dashboard/work"),
        ),
    )


def _click_work_action(
    page: Page,
    *,
    button_name: str,
    endpoint: str,
    checkpoint: str,
) -> None:
    button = page.get_by_role("button", name=button_name, exact=True)
    expect(button).to_be_visible(timeout=15_000)
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and urlsplit(response.url).path == endpoint,
        timeout=15_000,
    ) as response_info:
        button.click()
    response = response_info.value
    assert response.status == 200, (
        f"{checkpoint}: действие не завершилось успешно, HTTP {response.status}."
    )


def _uat_op_002(request: pytest.FixtureRequest) -> None:
    temporary_operator = request.getfixturevalue("temporary_operator")
    browser = request.getfixturevalue("browser")
    browser_context_args = request.getfixturevalue("browser_context_args")
    playwright = request.getfixturevalue("playwright")
    settings: Settings = request.getfixturevalue("test_settings")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    with operator_work_harness(
        temporary_operator=temporary_operator,
        browser=browser,
        browser_context_args=browser_context_args,
        playwright=playwright,
        test_settings=settings,
        login_rate_guard=login_rate_guard,
    ) as harness:
        harness.open_work_page(settings.web_base_url)
        _click_work_action(
            harness.page,
            button_name="Начать смену",
            endpoint="/v1/operator-work/shift",
            checkpoint="[UAT-OP-002] начало смены",
        )
        expect(harness.page.get_by_text("Работает", exact=True)).to_be_visible(
            timeout=15_000
        )
        _click_work_action(
            harness.page,
            button_name="Перерыв",
            endpoint="/v1/operator-work/break",
            checkpoint="[UAT-OP-002] начало перерыва",
        )
        expect(harness.page.get_by_text("На перерыве", exact=True)).to_be_visible(
            timeout=15_000
        )
        _click_work_action(
            harness.page,
            button_name="Завершить перерыв",
            endpoint="/v1/operator-work/break",
            checkpoint="[UAT-OP-002] завершение перерыва",
        )
        expect(harness.page.get_by_text("Работает", exact=True)).to_be_visible(
            timeout=15_000
        )
        _click_work_action(
            harness.page,
            button_name="Завершить смену",
            endpoint="/v1/operator-work/shift",
            checkpoint="[UAT-OP-002] завершение смены",
        )
        expect(harness.page.get_by_text("Не работает", exact=True)).to_be_visible(
            timeout=15_000
        )
        harness.page.reload(wait_until="commit")
        expect(harness.page.get_by_text("Не работает", exact=True)).to_be_visible(
            timeout=15_000
        )


def _uat_rop_006(request: pytest.FixtureRequest) -> None:
    temporary_operator = request.getfixturevalue("temporary_operator")
    browser = request.getfixturevalue("browser")
    browser_context_args = request.getfixturevalue("browser_context_args")
    playwright = request.getfixturevalue("playwright")
    settings: Settings = request.getfixturevalue("test_settings")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    authorized_page_factory = request.getfixturevalue("authorized_page_factory")
    full_name = f"{temporary_operator.first_name} {temporary_operator.last_name}"

    with operator_work_harness(
        temporary_operator=temporary_operator,
        browser=browser,
        browser_context_args=browser_context_args,
        playwright=playwright,
        test_settings=settings,
        login_rate_guard=login_rate_guard,
    ) as harness:
        harness.open_work_page(settings.web_base_url)
        _click_work_action(
            harness.page,
            button_name="Начать смену",
            endpoint="/v1/operator-work/shift",
            checkpoint="[UAT-ROP-006] начало смены оператора",
        )
        expect(harness.page.get_by_text("Работает", exact=True)).to_be_visible(
            timeout=15_000
        )

        rop_page: Page = authorized_page_factory("rop")
        with rop_page.expect_response(
            lambda response: response.request.method == "GET"
            and urlsplit(response.url).path == "/v1/operator-work/weekly",
            timeout=15_000,
        ) as open_attendance_info:
            rop_page.goto(
                f"{settings.web_base_url}/dashboard/attendance",
                wait_until="commit",
            )
        assert open_attendance_info.value.status == 200, (
            "[UAT-ROP-006] ROP не получил посещаемость после начала смены."
        )
        open_row = rop_page.get_by_role("row").filter(has_text=full_name)
        expect(open_row).to_have_count(1, timeout=15_000)
        expect(open_row.get_by_text("Открыта", exact=True)).to_be_visible()

        _click_work_action(
            harness.page,
            button_name="Завершить смену",
            endpoint="/v1/operator-work/shift",
            checkpoint="[UAT-ROP-006] завершение смены оператора",
        )
        expect(harness.page.get_by_text("Не работает", exact=True)).to_be_visible(
            timeout=15_000
        )
        with rop_page.expect_response(
            lambda response: response.request.method == "GET"
            and urlsplit(response.url).path == "/v1/operator-work/weekly",
            timeout=15_000,
        ) as closed_attendance_info:
            rop_page.reload(wait_until="commit")
        assert closed_attendance_info.value.status == 200, (
            "[UAT-ROP-006] ROP не получил итог завершённой смены."
        )
        closed_row = rop_page.get_by_role("row").filter(has_text=full_name)
        expect(closed_row).to_have_count(1, timeout=15_000)
        expect(closed_row.get_by_text("Открыта", exact=True)).to_have_count(0)


def _uat_op_009(request: pytest.FixtureRequest) -> None:
    from autotests.tests.web.test_tc_065_operator_deals import (
        OperatorDealsContractError,
        test_tc_065_operator_deals_show_status_attempts_and_details,
    )

    try:
        test_tc_065_operator_deals_show_status_attempts_and_details(
            request.getfixturevalue("authorized_page_factory"),
            request.getfixturevalue("test_settings"),
        )
    except OperatorDealsContractError as error:
        _gate("UAT-OP-009", str(error))


HANDLERS: dict[str, Handler] = {
    "UAT-SYS-001": _uat_sys_001,
    "UAT-SYS-002": _uat_sys_002,
    "UAT-COM-001": _uat_com_001,
    "UAT-COM-002": _uat_com_002,
    "UAT-LND-001": _uat_lnd_001,
    "UAT-SA-001": _uat_sa_001,
    "UAT-SA-002": _uat_sa_002,
    "UAT-ROP-001": _uat_rop_001,
    "UAT-ROP-002": _uat_rop_002,
    "UAT-ROP-006": _uat_rop_006,
    "UAT-OP-001": _uat_op_001,
    "UAT-OP-002": _uat_op_002,
    "UAT-OP-009": _uat_op_009,
}


GATES: dict[str, str] = {
    "UAT-LND-002": "нужен удаляемый канал demo-заявок и явное разрешение OPERATOR_AI_UAT_ALLOW_DEMO_MUTATION=true",
    "UAT-SA-003": "нужны отдельные AmoCRM credentials и разрешённый ежедневный cleanup",
    "UAT-SA-004": "нужны отдельные OnlinePBX credentials и разрешённый ежедневный cleanup",
    "UAT-SA-005": "нужно разрешение OPERATOR_AI_UAT_ALLOW_PLAN_MUTATION=true",
    "UAT-SA-006": "нужны три удаляемые тестовые компании и подготовленные позитивные данные тарифов",
    "UAT-ROP-003": "нужны две тестовые AmoCRM-воронки и разрешение изменять назначения",
    "UAT-ROP-004": "нужна тестовая AmoCRM-структура и разрешение изменять подсказки",
    "UAT-ROP-005": "нужно разрешение изменять и восстанавливать общие критерии очереди",
    "UAT-OP-004": "нужен удаляемый уникальный тестовый лид в очереди",
    "UAT-OP-007": "нужен безопасный setup готовой AI-сессии",
    "UAT-OP-008": "нужны два удаляемых тестовых лида",
    "UAT-FLOW-001": "нужен setup пяти независимых тестовых лидов",
    "UAT-FLOW-002": "нужен setup наступившей встречи без ожидания времени",
    "UAT-FLOW-003": "нужен setup лида с тремя попытками и безопасный переход",
}


def _marks_for(case: UATCase) -> list[Any]:
    marks: list[Any] = [
        pytest.mark.daily_uat,
        pytest.mark.positive,
        pytest.mark.serial,
        pytest.mark.uat_id(case.id),
    ]
    marks.append({"P0": pytest.mark.critical, "P1": pytest.mark.high, "P2": pytest.mark.medium}[case.priority])
    if case.layer == "api":
        marks.append(pytest.mark.api)
    else:
        marks.append(pytest.mark.web)
        if case.layer == "hybrid_ui_api":
            marks.append(pytest.mark.api)
    if case.execution_state == "blocked_defect":
        defects = ", ".join(case.blocked_by)
        marks.append(pytest.mark.skip(reason=f"BLOCKED_DEFECT [{case.id}]: {defects}"))
    return marks


UAT_PARAMS = [
    pytest.param(case, id=case.id, marks=_marks_for(case))
    for case in CATALOG.cases
]


@pytest.mark.parametrize("uat_case", UAT_PARAMS)
def test_daily_happy_path_case(
    request: pytest.FixtureRequest,
    uat_case: UATCase,
) -> None:
    handler = HANDLERS.get(uat_case.id)
    if handler is None:
        _gate(uat_case.id, GATES.get(uat_case.id, "UAT-обработчик не реализован"))
    handler(request)
