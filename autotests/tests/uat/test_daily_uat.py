from __future__ import annotations

import os
import re
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import replace
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

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
from autotests.support.operator_api import (
    cleanup_users_by_username,
    list_extensions,
    list_operator_pipelines,
)
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


def _api_json(
    response: Any,
    *,
    checkpoint: str,
    expected_status: int = 200,
) -> dict[str, Any]:
    assert response.status == expected_status, (
        f"{checkpoint}: ожидали HTTP {expected_status}, получили "
        f"{response.status}."
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"{checkpoint}: ожидали JSON-объект, получили {type(body).__name__}."
    )
    return body


def _api_items(response: Any, *, checkpoint: str) -> list[dict[str, Any]]:
    body = _api_json(response, checkpoint=checkpoint)
    items = body.get("items")
    assert isinstance(items, list) and all(isinstance(item, dict) for item in items), (
        f"{checkpoint}: ответ не содержит корректный массив items."
    )
    return items


def _role_request(
    request: pytest.FixtureRequest,
    role: str,
) -> APIRequestContext:
    playwright = request.getfixturevalue("playwright")
    settings: Settings = request.getfixturevalue("test_settings")
    role_api_token = request.getfixturevalue("role_api_token")
    return playwright.request.new_context(
        base_url=settings.require_api_base_url(),
        extra_http_headers={
            "Authorization": f"Bearer {role_api_token(role)}",
            "Content-Type": "application/json",
        },
    )


def _current_rop(rop_request: APIRequestContext) -> dict[str, Any]:
    return _api_json(
        rop_request.get("/v1/auth/me"),
        checkpoint="[UAT] текущий ROP",
    )


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


def _uat_lnd_002(request: pytest.FixtureRequest) -> None:
    _env_gate(
        "UAT-LND-002",
        ("OPERATOR_AI_LANDING_BASE_URL",),
        "нужен URL тестового Landing",
    )
    page: Page = request.getfixturevalue("page")
    settings: Settings = request.getfixturevalue("test_settings")
    landing_url = os.environ["OPERATOR_AI_LANDING_BASE_URL"].rstrip("/")
    unique = uuid4().hex
    lead_name = f"UAT Demo {unique[:6]}"
    company = f"UAT Landing {unique[:8]}"
    phone = f"+99890{uuid4().int % 10_000_000:07d}"
    username = f"UAT-LND-{unique[:8]}"
    password = f"UAT!{unique[:12]}"
    lead_id = ""
    superadmin_page: Page | None = None
    superadmin_api: UserApi | None = None
    superadmin_request = _role_request(request, "superadmin")

    try:
        page.goto(f"{landing_url}/#demo", wait_until="networkidle")
        page.locator('input[name="ism"]').fill(lead_name)
        page.locator('input[name="telefon_raqam"]').fill(phone)
        page.locator('input[name="kampaniya_nomi"]').fill(company)
        page.locator('select[name="crm"]').select_option("amocrm")
        page.locator('select[name="tarif"]').select_option("full_ai")
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path == "/v1/leads",
            timeout=15_000,
        ) as submitted_info:
            page.get_by_role("button", name="Demo so'rash", exact=True).click()
        submitted = submitted_info.value
        assert submitted.status == 200, (
            "Landing не принял demo-заявку: "
            f"HTTP {submitted.status}."
        )
        submitted_body = submitted.json()
        lead_id = str(submitted_body.get("id") or "")
        assert lead_id, "Landing не вернул ID созданной demo-заявки."
        expect(page.get_by_role("status")).to_contain_text("So'rov qabul qilindi")

        superadmin_page = request.getfixturevalue("authorized_page_factory")(
            "superadmin"
        )
        superadmin_api = UserApi.from_authorized_page(
            superadmin_page,
            settings.web_base_url,
            discovery_path=RopListPage.PATH,
        )
        superadmin_page.goto(
            f"{settings.web_base_url}/dashboard/leads/{lead_id}",
            wait_until="domcontentloaded",
        )
        expect(superadmin_page.get_by_text(lead_name, exact=True)).to_be_visible(
            timeout=15_000
        )
        expect(superadmin_page.get_by_text(company, exact=True)).to_be_visible()
        expect(superadmin_page.get_by_text(phone, exact=True)).to_be_visible()
        expect(superadmin_page.get_by_text("Full AI", exact=True)).to_be_visible()

        superadmin_page.get_by_role(
            "button", name="Создать РОП из лида", exact=True
        ).click()
        dialog = superadmin_page.get_by_role(
            "dialog", name="Создать РОП из лида"
        )
        expect(dialog).to_be_visible()
        dialog.locator('input[name="username"]').fill(username)
        dialog.locator('input[name="password"]').fill(password)
        with superadmin_page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path == "/v1/rops",
            timeout=15_000,
        ) as created_info:
            dialog.get_by_role("button", name="Создать РОП", exact=True).click()
        assert created_info.value.status == 200, (
            "Superadmin не смог превратить demo-заявку в ROP."
        )
        expect(
            superadmin_page.get_by_text(
                "РОП создан, лид сконвертирован", exact=True
            )
        ).to_be_visible(timeout=15_000)

        lead = _api_json(
            superadmin_request.get(f"/v1/leads/{lead_id}"),
            checkpoint="[UAT-LND-002] сконвертированная заявка",
        )
        assert lead.get("converted_at"), "Demo-заявка не отмечена сконвертированной."
        assert lead.get("tariff") == "full_ai", "Выбранный Landing-тариф потерян."
    finally:
        cleanup_errors: list[Exception] = []
        try:
            if superadmin_api is not None:
                try:
                    cleanup_rops_by_username(
                        superadmin_api,
                        username,
                        checkpoint="[UAT-LND-002 cleanup ROP]",
                    )
                except Exception as error:
                    cleanup_errors.append(error)
            if lead_id:
                try:
                    deleted = superadmin_request.delete(f"/v1/leads/{lead_id}")
                    assert deleted.status == 200, (
                        "[UAT-LND-002 cleanup] demo-заявка не удалена: "
                        f"HTTP {deleted.status}: {deleted.text()}"
                    )
                except Exception as error:
                    cleanup_errors.append(error)
        finally:
            superadmin_request.dispose()
        if cleanup_errors:
            raise cleanup_errors[0]


@contextmanager
def _uat_fixture_leads(
    request: pytest.FixtureRequest,
    specs: list[dict[str, Any]],
):
    temporary_operator = request.getfixturevalue("temporary_operator")
    rop_request: APIRequestContext = temporary_operator.rop_request
    settings: Settings = request.getfixturevalue("test_settings")
    playwright = request.getfixturevalue("playwright")
    browser = request.getfixturevalue("browser")
    browser_context_args = request.getfixturevalue("browser_context_args")
    login_rate_guard = request.getfixturevalue("login_rate_guard")
    items: list[dict[str, Any]] = []
    assigned_pipeline_id = ""
    try:
        pipelines = _api_items(
            rop_request.get("/v1/calling/assignable-pipelines"),
            checkpoint="[UAT fixture] доступные воронки",
        )
        required_classes = {
            str(spec.get("status_class") or "")
            for spec in specs
        }
        if "uchrashuv" in required_classes:
            required_classes.add("bugun_keladi")
        if any(
            spec.get("status_class") == "kotarmadi"
            and int(spec.get("attempts") or 0) == 3
            for spec in specs
        ):
            required_classes.add("sifatsiz")

        compatible_pipelines: list[dict[str, Any]] = []
        pipeline_classes: dict[str, set[str]] = {}
        for pipeline in pipelines:
            pipeline_id = str(pipeline.get("id") or "")
            if not pipeline_id:
                continue
            statuses = _api_items(
                rop_request.get(
                    "/v1/amocrm/statuses",
                    params={"pipeline_id": pipeline_id},
                ),
                checkpoint=f"[UAT fixture] статусы воронки {pipeline_id}",
            )
            classes = {
                _uat_status_class(str(status.get("name") or ""))
                for status in statuses
            }
            pipeline_classes[pipeline_id] = classes
            if required_classes <= classes:
                compatible_pipelines.append(pipeline)

        assert compatible_pipelines, (
            "Нет staging-воронки со статусами, нужными сценарию: "
            f"{sorted(required_classes)}; найденные классы: {pipeline_classes}."
        )
        assignment_results: list[str] = []
        for pipeline in compatible_pipelines:
            pipeline_id = str(pipeline.get("id") or "")
            if not pipeline_id:
                continue
            assigned = rop_request.post(
                "/v1/uat/fixtures/operator-pipelines",
                data={
                    "operator_id": temporary_operator.id,
                    "pipeline_id": pipeline_id,
                },
            )
            assignment_results.append(f"{pipeline_id}: HTTP {assigned.status}")
            if assigned.status == 200:
                assigned_pipeline_id = pipeline_id
                break
        assert assigned_pipeline_id, (
            "Не удалось назначить временного Operator ни на одну staging-воронку: "
            f"{assignment_results}."
        )

        with operator_work_harness(
            temporary_operator=temporary_operator,
            browser=browser,
            browser_context_args=browser_context_args,
            playwright=playwright,
            test_settings=settings,
            login_rate_guard=login_rate_guard,
        ) as harness:
            try:
                created = rop_request.post(
                    "/v1/uat/fixtures/leads",
                    data={
                        "operator_id": temporary_operator.id,
                        "run_id": f"daily-{uuid4().hex[:10]}",
                        "leads": specs,
                    },
                )
                body = _api_json(
                    created,
                    checkpoint="[UAT fixture] создание временных лидов",
                )
                raw_items = body.get("items")
                assert isinstance(raw_items, list) and len(raw_items) == len(specs), (
                    "Fixture API создал не все запрошенные лиды."
                )
                items = [item for item in raw_items if isinstance(item, dict)]
                assert len(items) == len(specs)
                yield items, harness.operator_request, rop_request, harness.page
            finally:
                for item in reversed(items):
                    lead_id = str(item.get("id") or "")
                    if not lead_id:
                        continue
                    deleted = rop_request.delete(f"/v1/uat/fixtures/leads/{lead_id}")
                    assert deleted.status == 200, (
                        f"[UAT fixture cleanup] лид {lead_id} не удалён: "
                        f"HTTP {deleted.status}: {deleted.text()}"
                    )
    finally:
        if assigned_pipeline_id:
            unassigned = rop_request.delete(
                "/v1/operator-pipelines/"
                f"{temporary_operator.id}/{assigned_pipeline_id}"
            )
            assert unassigned.status == 200, (
                "[UAT fixture cleanup] назначение временного Operator не удалено: "
                f"HTTP {unassigned.status}: {unassigned.text()}"
            )


def _open_calling_modal(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/dashboard/calling", wait_until="domcontentloaded")
    expect(page.get_by_role("progressbar")).to_have_count(0, timeout=20_000)
    page.get_by_role("button", name="Начать обзвон", exact=True).click()


def _uat_status_class(name: str) -> str:
    normalized = name.strip().lower()
    for apostrophe in ("'", "’", "`", "ʻ", "ʼ"):
        normalized = normalized.replace(apostrophe, "")
    if "kotarmadi" in normalized:
        return "kotarmadi"
    if "chala" in normalized:
        return "chala"
    if "keyingi" in normalized and "qongiroq" in normalized:
        return "keyingi_qongiroq"
    if "bugun" in normalized:
        return "bugun_keladi"
    if "uchrashuv" in normalized:
        return "uchrashuv"
    if "markaz" in normalized:
        return "markazga_keldi"
    if "sifatsiz" in normalized:
        return "sifatsiz"
    if "yangi" in normalized:
        return "yangi"
    return "other"


def _uat_op_004(request: pytest.FixtureRequest) -> None:
    settings: Settings = request.getfixturevalue("test_settings")
    with _uat_fixture_leads(
        request, [{"key": "queue", "status_class": "yangi"}]
    ) as (items, operator_request, _, page):
        count = _api_json(
            operator_request.get("/v1/calling/queue"),
            checkpoint="[UAT-OP-004] количество лидов",
        )
        assert int(count.get("count") or 0) >= 1, "Очередь не показывает тестового лида."
        with page.expect_response(
            lambda response: urlsplit(response.url).path == "/v1/calling/next"
        ) as next_info:
            _open_calling_modal(page, settings.web_base_url)
        next_body = next_info.value.json()
        guideline = next_body.get("guideline") or {}
        assert (guideline.get("lead") or {}).get("id") == items[0].get("id")
        expect(page.get_by_text(str(items[0]["name"]), exact=True).first).to_be_visible()
        expect(page.get_by_text("Цель и обязательные поля", exact=True)).to_be_visible()
        assert (guideline.get("reason") or {}).get("status_class") == "yangi"


def _uat_op_007(request: pytest.FixtureRequest) -> None:
    settings: Settings = request.getfixturevalue("test_settings")
    with _uat_fixture_leads(
        request,
        [{"key": "ai-ready", "status_class": "yangi", "ready_ai_result": True}],
    ) as (items, _, _, page):
        captured: list[dict[str, Any]] = []

        def fulfill_confirm(route: Any) -> None:
            captured.append(route.request.post_data_json or {})
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"id":"uat","state":"synced"}',
            )

        page.route("**/v1/calling/sessions/*/confirm", fulfill_confirm)
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path.endswith("/confirm"),
            timeout=30_000,
        ) as confirmed_info:
            _open_calling_modal(page, settings.web_base_url)
            expect(
                page.get_by_text("Рекомендация ИИ — подтвердите", exact=True)
            ).to_be_visible(timeout=15_000)
            expect(page.get_by_text("UAT: mijoz", exact=False)).to_be_visible()
            expect(page.get_by_text("через 20 сек", exact=True)).to_be_visible()
        assert confirmed_info.value.status == 200, (
            "UI не завершил автосохранение AI-результата."
        )
        assert len(captured) == 1, "UI не отправил AI-результат после таймера."
        assert items[0].get("session_id"), "Fixture не подготовил AI-сессию."


def _uat_op_008(request: pytest.FixtureRequest) -> None:
    settings: Settings = request.getfixturevalue("test_settings")
    with _uat_fixture_leads(
        request,
        [
            {"key": "skip-first", "status_class": "yangi"},
            {"key": "skip-second", "status_class": "yangi"},
        ],
    ) as (items, _, _, page):
        _open_calling_modal(page, settings.web_base_url)
        expect(page.get_by_text(str(items[0]["name"]), exact=True).first).to_be_visible(
            timeout=15_000
        )
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path.endswith("/skip")
        ) as skipped_info:
            page.get_by_role("button", name="Пропустить", exact=True).click()
        assert skipped_info.value.status == 200
        expect(page.get_by_text(str(items[1]["name"]), exact=True).first).to_be_visible(
            timeout=15_000
        )


def _uat_flow_001(request: pytest.FixtureRequest) -> None:
    now = datetime.now(timezone.utc).isoformat()
    expected = [
        ("bugun_keladi", {"arrival_at": now}),
        ("keyingi_qongiroq", {"callback_at": now}),
        ("chala", {}),
        ("kotarmadi", {}),
        ("yangi", {}),
    ]
    specs = [
        {"key": f"rank-{index}", "status_class": status_class, **extra}
        for index, (status_class, extra) in enumerate(expected, 1)
    ]
    with _uat_fixture_leads(request, specs) as (_, operator_request, _, _):
        actual: list[str] = []
        for _ in expected:
            next_body = _api_json(
                operator_request.get("/v1/calling/next"),
                checkpoint="[UAT-FLOW-001] следующий лид",
            )
            guideline = next_body.get("guideline") or {}
            actual.append(str((guideline.get("reason") or {}).get("status_class")))
            session_id = str((guideline.get("session") or {}).get("id") or "")
            assert session_id
            skipped = operator_request.post(
                f"/v1/calling/sessions/{session_id}/skip", data={}
            )
            assert skipped.status == 200
        assert actual == [status for status, _ in expected], (
            f"Неверный порядок очереди: {actual}."
        )


def _uat_flow_002(request: pytest.FixtureRequest) -> None:
    settings: Settings = request.getfixturevalue("test_settings")
    now = datetime.now(timezone.utc).isoformat()
    with _uat_fixture_leads(
        request,
        [{"key": "meeting", "status_class": "uchrashuv", "appointment_at": now}],
    ) as (items, _, rop_request, page):
        transitioned = _api_json(
            rop_request.post(
                "/v1/uat/fixtures/transitions",
                data={"lead_ids": [items[0]["id"]]},
            ),
            checkpoint="[UAT-FLOW-002] переход встречи",
        )
        assert transitioned["items"][0]["status_class"] == "bugun_keladi"
        _open_calling_modal(page, settings.web_base_url)
        expect(page.get_by_text(str(items[0]["name"]), exact=True).first).to_be_visible(
            timeout=15_000
        )
        expect(page.get_by_text("Придёт сегодня", exact=False)).to_be_visible()


def _uat_flow_003(request: pytest.FixtureRequest) -> None:
    with _uat_fixture_leads(
        request,
        [{"key": "fourth-attempt", "status_class": "kotarmadi", "attempts": 3}],
    ) as (items, operator_request, rop_request, _):
        transitioned = _api_json(
            rop_request.post(
                "/v1/uat/fixtures/transitions",
                data={"lead_ids": [items[0]["id"]]},
            ),
            checkpoint="[UAT-FLOW-003] четвёртая попытка",
        )
        assert transitioned["items"][0]["status_class"] == "sifatsiz"
        preview = _api_json(
            operator_request.get("/v1/calling/queue/preview"),
            checkpoint="[UAT-FLOW-003] очередь после перехода",
        )
        visible_ids = {
            str(item.get("lead_id") or "")
            for group in (preview.get("due", []), preview.get("scheduled", []))
            for item in group
            if isinstance(item, dict)
        }
        assert str(items[0]["id"]) not in visible_ids, (
            "Лид Sifatsiz остался в очереди Operator."
        )


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


def _configured_rop_for_integration(
    superadmin_request: APIRequestContext,
    rop_request: APIRequestContext,
    *,
    config_path: str,
    checkpoint: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    rop = _current_rop(rop_request)
    rop_id = str(rop.get("id") or "")
    assert rop_id, f"{checkpoint}: у текущего ROP отсутствует ID."
    configs = _api_items(
        superadmin_request.get(config_path, params={"page": 1, "perPage": 100}),
        checkpoint=f"{checkpoint} список конфигураций",
    )
    config = next(
        (item for item in configs if str(item.get("rop_id") or "") == rop_id),
        None,
    )
    assert config is not None, (
        f"{checkpoint}: для выделенного staging ROP интеграция не подключена."
    )
    user = _api_json(
        superadmin_request.get(f"/v1/users/{rop_id}"),
        checkpoint=f"{checkpoint} карточка ROP",
    )
    return rop, user, config


def _uat_sa_003(request: pytest.FixtureRequest) -> None:
    rop_request = request.getfixturevalue("rop_api_request")
    superadmin_request = _role_request(request, "superadmin")
    page: Page = request.getfixturevalue("authorized_page_factory")("superadmin")
    settings: Settings = request.getfixturevalue("test_settings")
    try:
        _, rop_user, config = _configured_rop_for_integration(
            superadmin_request,
            rop_request,
            config_path="/v1/amocrm/configs",
            checkpoint="[UAT-SA-003] AmoCRM",
        )
        assert config.get("is_active") is True, (
            "[UAT-SA-003] подключение AmoCRM выключено."
        )
        company_name = str(
            rop_user.get("company_name")
            or (rop_user.get("company") or {}).get("name")
            or ""
        )
        full_name = " ".join(
            str(rop_user.get(key) or "").strip()
            for key in ("first_name", "last_name")
        ).strip()
        assert company_name and full_name

        rop_list = RopListPage(page)
        page.goto(f"{settings.web_base_url}{RopListPage.PATH}", wait_until="commit")
        expect(rop_list.heading).to_be_visible(timeout=20_000)
        row = rop_list.row_by_company(company_name)
        expect(row).to_have_count(1)
        expect(row.get_by_role("cell").nth(2)).to_contain_text("Подключено")
        dialog = rop_list.open_amocrm_dialog(
            company_name,
            user_full_name=full_name,
        )
        expect(dialog.dialog).to_contain_text("AmoCRM уже подключён")
        expect(dialog.dialog).to_contain_text(str(config.get("domain") or ""))
        dialog.dialog.get_by_role("button", name="Закрыть", exact=True).click()

        synced = _api_items(
            rop_request.post("/v1/amocrm/pipelines/sync"),
            checkpoint="[UAT-SA-003] синхронизация воронок",
        )
        assert synced, "[UAT-SA-003] AmoCRM не вернула ни одной воронки."
        selected = _api_json(
            rop_request.get("/v1/amocrm/pipelines/selected"),
            checkpoint="[UAT-SA-003] выбранная воронка",
        )
        selected_id = str(selected.get("id") or "")
        assert selected_id
        statuses = _api_items(
            rop_request.get(
                "/v1/amocrm/statuses",
                params={"pipeline_id": selected_id},
            ),
            checkpoint="[UAT-SA-003] статусы выбранной воронки",
        )
        forms = _api_items(
            rop_request.get("/v1/amocrm/forms"),
            checkpoint="[UAT-SA-003] группы полей",
        )
        assert statuses, "[UAT-SA-003] выбранная воронка не содержит статусов."
        assert forms, "[UAT-SA-003] AmoCRM не вернула группы полей."
        form_id = str(forms[0].get("id") or "")
        fields = _api_items(
            rop_request.get(f"/v1/amocrm/forms/{form_id}/fields"),
            checkpoint="[UAT-SA-003] поля формы",
        )
        assert fields, "[UAT-SA-003] выбранная группа AmoCRM не содержит полей."

        rules_page: Page = request.getfixturevalue("authorized_page_factory")("rop")
        rules_page.goto(
            f"{settings.web_base_url}/dashboard/dynamic-form",
            wait_until="commit",
        )
        expect(
            rules_page.get_by_role("heading", name="Статусы лида", exact=True)
        ).to_be_visible(timeout=20_000)
        expect(
            rules_page.get_by_role("heading", name="Поля формы", exact=True)
        ).to_be_visible(timeout=20_000)
        expect(
            rules_page.get_by_text(str(selected.get("name") or ""), exact=True).first
        ).to_be_visible(timeout=20_000)
    finally:
        superadmin_request.dispose()


def _uat_sa_004(request: pytest.FixtureRequest) -> None:
    rop_request = request.getfixturevalue("rop_api_request")
    superadmin_request = _role_request(request, "superadmin")
    page: Page = request.getfixturevalue("authorized_page_factory")("superadmin")
    settings: Settings = request.getfixturevalue("test_settings")
    try:
        _, rop_user, config = _configured_rop_for_integration(
            superadmin_request,
            rop_request,
            config_path="/v1/onlinepbx/configs",
            checkpoint="[UAT-SA-004] OnlinePBX",
        )
        company_name = str(
            rop_user.get("company_name")
            or (rop_user.get("company") or {}).get("name")
            or ""
        )
        full_name = " ".join(
            str(rop_user.get(key) or "").strip()
            for key in ("first_name", "last_name")
        ).strip()
        assert company_name and full_name

        rop_list = RopListPage(page)
        page.goto(f"{settings.web_base_url}{RopListPage.PATH}", wait_until="commit")
        expect(rop_list.heading).to_be_visible(timeout=20_000)
        row = rop_list.row_by_company(company_name)
        expect(row).to_have_count(1)
        expect(row.get_by_role("cell").nth(3)).to_contain_text("Подключено")
        dialog = rop_list.open_onlinepbx_dialog(
            company_name,
            user_full_name=full_name,
        )
        expect(dialog.dialog).to_contain_text("OnlinePBX уже подключён")
        expect(dialog.dialog).to_contain_text(str(config.get("domain") or ""))
        dialog.dialog.get_by_role("button", name="Закрыть", exact=True).click()

        extensions = list_extensions(
            rop_request,
            checkpoint="[UAT-SA-004] внутренние номера",
        )
        enabled = [
            item
            for item in extensions
            if item.get("enabled") is True and str(item.get("extension") or "")
        ]
        assert enabled, "[UAT-SA-004] OnlinePBX не вернула активные extensions."

        operators_page: Page = request.getfixturevalue("authorized_page_factory")("rop")
        operator_list = OperatorListPage(operators_page)
        operator_list.open(settings.web_base_url)
        expect(operator_list.heading).to_be_visible(timeout=20_000)
        create_dialog = operator_list.open_create_dialog()
        expect(create_dialog.extension_select).to_be_visible(timeout=20_000)
        create_dialog.open_extension_options()
        expect(
            create_dialog.extension_option(str(enabled[0]["extension"]))
        ).to_be_visible()
        operators_page.keyboard.press("Escape")
        create_dialog.cancel_button.click()
    finally:
        superadmin_request.dispose()


def _uat_sa_005(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("superadmin")
    settings: Settings = request.getfixturevalue("test_settings")
    superadmin_request = _role_request(request, "superadmin")
    plans_page = None
    original: dict[str, Any] | None = None
    try:
        plans = _api_items(
            superadmin_request.get("/v1/plans"),
            checkpoint="[UAT-SA-005] исходные тарифы",
        )
        original = next((item for item in plans if item.get("is_active") is True), None)
        assert original is not None, "[UAT-SA-005] нет активного staging-тарифа."
        code = str(original.get("code") or "")
        original_name = str(original.get("name") or "")
        assert code and original_name
        suffix = uuid4().hex[:6]
        changed_name = f"UAT {suffix} {original_name}"
        changed_price = int(original.get("price") or 0) + 1
        changed_description = f"UAT {suffix}: проверка публикации тарифа"
        changed_features = [f"UAT {suffix}: функция доступна"]

        from autotests.pages.plans_page import PlansPage

        plans_page = PlansPage(page)
        plans_page.open(settings.web_base_url)
        expect(plans_page.heading).to_be_visible(timeout=20_000)
        dialog = plans_page.open_edit_dialog(original_name)
        expect(dialog.dialog).to_be_visible()
        dialog.name_input.fill(changed_name)
        dialog.price_input.fill(str(changed_price))
        dialog.description_input.fill(changed_description)
        dialog.features_input.fill("\n".join(changed_features))
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/plans/{code}"
        ) as saved_info:
            dialog.save_button.click()
        assert saved_info.value.status == 200, (
            "[UAT-SA-005] Super-admin не смог сохранить staging-тариф."
        )
        expect(plans_page.card_by_name(changed_name)).to_have_count(1)

        published = _api_items(
            superadmin_request.get("/v1/plans"),
            checkpoint="[UAT-SA-005] опубликованные тарифы",
        )
        changed = next((item for item in published if item.get("code") == code), None)
        assert changed is not None
        assert changed.get("name") == changed_name
        assert changed.get("price") == changed_price
        assert changed.get("description") == changed_description
        assert changed.get("features") == changed_features
    finally:
        if original is not None:
            code = str(original.get("code") or "")
            if code:
                restored = superadmin_request.patch(
                    f"/v1/plans/{code}",
                    data={
                        "name": original.get("name"),
                        "price": original.get("price"),
                        "description": original.get("description"),
                        "features": original.get("features"),
                        "is_active": original.get("is_active"),
                        "sort": original.get("sort"),
                    },
                )
                assert restored.status == 200, (
                    "[UAT-SA-005 cleanup] не удалось восстановить staging-тариф."
                )
                if plans_page is not None:
                    page.reload(wait_until="commit")
                    expect(
                        plans_page.card_by_name(str(original.get("name") or ""))
                    ).to_have_count(1, timeout=20_000)
        superadmin_request.dispose()


def _uat_sa_006(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("superadmin")
    settings: Settings = request.getfixturevalue("test_settings")
    superadmin_request = _role_request(request, "superadmin")
    rop_list = RopListPage(page)
    created_ids: list[str] = []
    tariff_options = (
        ("taxlil_dashboard", "Аналитика"),
        ("taxlil_dashboard_auto_call", "Аналитика + Авто-звонок"),
        ("full_ai", "Full AI"),
    )
    try:
        active_codes = {
            str(item.get("code") or "")
            for item in _api_items(
                superadmin_request.get("/v1/plans"),
                checkpoint="[UAT-SA-006] действующие тарифы",
            )
            if item.get("is_active") is True
        }
        assert active_codes == {code for code, _ in tariff_options}, (
            "[UAT-SA-006] должны быть активны все три фиксированных тарифа."
        )
        page.goto(f"{settings.web_base_url}{RopListPage.PATH}", wait_until="commit")
        expect(rop_list.heading).to_be_visible(timeout=20_000)

        for index, (tariff_code, tariff_label) in enumerate(tariff_options):
            unique = uuid4().hex
            company_name = f"UAT Tariff {index + 1} {unique[:6]}"
            dialog = rop_list.open_create_dialog()
            dialog.fill(
                first_name="UAT",
                last_name=f"Tariff{index + 1}{unique[:4]}",
                phone=f"+99893{uuid4().int % 10_000_000:07d}",
                password=f"UAT!{unique[:12]}",
                username=f"UAT-PLAN-{unique[:8]}",
                company_name=company_name,
            )
            dialog.select_tariff(tariff_label)
            with page.expect_response(
                lambda response: response.request.method == "POST"
                and urlsplit(response.url).path == "/v1/rops"
            ) as created_info:
                dialog.create()
            created_response = created_info.value
            try:
                created_body = created_response.json()
            except Exception:
                created_body = {}
            created_id = str(
                (created_body.get("id") or "")
                if isinstance(created_body, dict)
                else ""
            )
            if created_id:
                created_ids.append(created_id)
            assert created_response.status == 200, (
                f"[UAT-SA-006:{tariff_code}] ROP не создан."
            )
            assert created_id, f"[UAT-SA-006:{tariff_code}] ответ не содержит ID."
            request_payload = created_response.request.post_data_json
            assert isinstance(request_payload, dict)
            assert request_payload.get("tariff") == tariff_code, (
                f"[UAT-SA-006:{tariff_code}] UI отправил другой тариф."
            )
            expect(rop_list.row_by_company(company_name)).to_have_count(1)
            persisted = _api_json(
                superadmin_request.get(f"/v1/users/{created_id}"),
                checkpoint=f"[UAT-SA-006:{tariff_code}] сохранённый ROP",
            )
            assert persisted.get("id") == created_id
            assert persisted.get("company_name") == company_name
    finally:
        for created_id in reversed(created_ids):
            deleted = superadmin_request.delete(f"/v1/users/{created_id}")
            assert deleted.status == 200, (
                f"[UAT-SA-006 cleanup] не удалён временный ROP {created_id}."
            )
        superadmin_request.dispose()


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


def _uat_rop_003(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("rop")
    settings: Settings = request.getfixturevalue("test_settings")
    rop_request = request.getfixturevalue("rop_api_request")
    temporary_operator = request.getfixturevalue("temporary_operator")
    pipelines = _api_items(
        rop_request.get("/v1/calling/assignable-pipelines"),
        checkpoint="[UAT-ROP-003] доступные воронки",
    )
    assert len(pipelines) >= 2, (
        "[UAT-ROP-003] для проверки нужны минимум две staging-воронки."
    )
    selected = pipelines[:2]
    selected_ids = {str(item.get("id") or "") for item in selected}
    assert len(selected_ids) == 2 and "" not in selected_ids
    original = list_operator_pipelines(
        rop_request,
        temporary_operator.id,
        checkpoint="[UAT-ROP-003] исходные назначения",
    )
    assert original == [], (
        "[UAT-ROP-003] временный Operator неожиданно получил назначения."
    )

    try:
        page.goto(
            f"{settings.web_base_url}/dashboard/operator-pipelines",
            wait_until="commit",
        )
        expect(
            page.get_by_role("heading", name="Настройка очереди", exact=True)
        ).to_be_visible(timeout=20_000)
        card = page.locator(".MuiCard-root").filter(
            has_text=f"{temporary_operator.first_name} {temporary_operator.last_name}"
        )
        expect(card).to_have_count(1)

        for pipeline in selected:
            pipeline_id = str(pipeline["id"])
            pipeline_name = str(pipeline.get("name") or "")
            with page.expect_response(
                lambda response: response.request.method == "POST"
                and urlsplit(response.url).path == "/v1/operator-pipelines"
            ) as assigned_info:
                card.get_by_text(pipeline_name, exact=True).click()
            assert assigned_info.value.status == 200, (
                f"[UAT-ROP-003] не назначена воронка {pipeline_id}."
            )

        assigned = list_operator_pipelines(
            rop_request,
            temporary_operator.id,
            checkpoint="[UAT-ROP-003] два назначения",
        )
        assert {str(item.get("pipeline_id") or "") for item in assigned} == selected_ids

        page.reload(wait_until="commit")
        expect(
            page.get_by_role("heading", name="Настройка очереди", exact=True)
        ).to_be_visible(timeout=20_000)
        reloaded_card = page.locator(".MuiCard-root").filter(
            has_text=f"{temporary_operator.first_name} {temporary_operator.last_name}"
        )
        expect(reloaded_card).to_have_count(1)
        removed = selected[0]
        removed_id = str(removed["id"])
        with page.expect_response(
            lambda response: response.request.method == "DELETE"
            and urlsplit(response.url).path
            == f"/v1/operator-pipelines/{temporary_operator.id}/{removed_id}"
        ) as removed_info:
            reloaded_card.get_by_text(str(removed.get("name") or ""), exact=True).click()
        assert removed_info.value.status == 200
        remaining = list_operator_pipelines(
            rop_request,
            temporary_operator.id,
            checkpoint="[UAT-ROP-003] одно назначение",
        )
        assert {str(item.get("pipeline_id") or "") for item in remaining} == {
            str(selected[1]["id"])
        }
    finally:
        current = list_operator_pipelines(
            rop_request,
            temporary_operator.id,
            checkpoint="[UAT-ROP-003 cleanup] текущие назначения",
        )
        cleanup_failures: list[str] = []
        for assignment in current:
            pipeline_id = str(assignment.get("pipeline_id") or "")
            response = rop_request.delete(
                f"/v1/operator-pipelines/{temporary_operator.id}/{pipeline_id}"
            )
            if response.status != 200:
                cleanup_failures.append(pipeline_id)
        assert not cleanup_failures, (
            "[UAT-ROP-003 cleanup] не восстановлены назначения: "
            f"{cleanup_failures}."
        )


def _uat_rop_004(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("rop")
    settings: Settings = request.getfixturevalue("test_settings")
    rop_request = request.getfixturevalue("rop_api_request")
    rop = _current_rop(rop_request)
    rop_id = str(rop.get("id") or "")
    selected = _api_json(
        rop_request.get("/v1/amocrm/pipelines/selected"),
        checkpoint="[UAT-ROP-004] выбранная воронка",
    )
    pipeline_id = str(selected.get("id") or "")
    statuses = _api_items(
        rop_request.get(
            "/v1/amocrm/statuses",
            params={"pipeline_id": pipeline_id},
        ),
        checkpoint="[UAT-ROP-004] статусы",
    )
    forms = _api_items(
        rop_request.get("/v1/amocrm/forms"),
        checkpoint="[UAT-ROP-004] формы",
    )
    assert statuses and forms
    form = next(
        (item for item in forms if "operator" in str(item.get("name") or "").lower()),
        forms[0],
    )
    form_id = str(form.get("id") or "")
    fields = _api_items(
        rop_request.get(f"/v1/amocrm/forms/{form_id}/fields"),
        checkpoint="[UAT-ROP-004] поля",
    )
    assert fields
    status = statuses[0]
    field = fields[0]
    status_id = str(status.get("id") or "")
    field_id = str(field.get("id") or "")
    status_priority = int(status.get("priority") or 1)
    field_required = bool(field.get("is_required"))
    description_body = _api_json(
        rop_request.get(f"/v1/users/{rop_id}/company-description"),
        checkpoint="[UAT-ROP-004] описание компании",
    )
    original_description = str(description_body.get("description") or "")
    marker = f"UAT-{uuid4().hex[:8]}"
    status_hint = f"{marker}: позитивная подсказка статуса"
    field_hint = f"{marker}: позитивная подсказка поля"
    company_description = f"{marker}: тестовое описание компании"

    try:
        page.goto(
            f"{settings.web_base_url}/dashboard/dynamic-form",
            wait_until="commit",
        )
        expect(
            page.get_by_role("heading", name="Статусы лида", exact=True)
        ).to_be_visible(timeout=20_000)
        expect(
            page.get_by_text(str(selected.get("name") or ""), exact=True).first
        ).to_be_visible(timeout=20_000)

        page.get_by_text(str(status.get("name") or ""), exact=True).first.click()
        status_dialog = page.get_by_role(
            "dialog", name="Редактировать статус", exact=True
        )
        expect(status_dialog).to_be_visible()
        status_dialog.get_by_label("Подсказка для ИИ", exact=True).fill(status_hint)
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/amocrm/statuses/{status_id}/hint"
        ) as status_info:
            status_dialog.get_by_role("button", name="Сохранить", exact=True).click()
        assert status_info.value.status == 200
        expect(page.get_by_text(status_hint, exact=True)).to_be_visible()

        field_name = str(field.get("name") or "")
        expect(page.get_by_text(field_name, exact=True).first).to_be_visible(timeout=20_000)
        page.get_by_text(field_name, exact=True).first.click()
        field_dialog = page.get_by_role(
            "dialog", name="Редактировать поле", exact=True
        )
        expect(field_dialog).to_be_visible()
        field_dialog.get_by_label("Подсказка для ИИ", exact=True).fill(field_hint)
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and urlsplit(response.url).path == f"/v1/amocrm/fields/{field_id}/hint"
        ) as field_info:
            field_dialog.get_by_role("button", name="Сохранить", exact=True).click()
        assert field_info.value.status == 200
        expect(page.get_by_text(field_hint, exact=True)).to_be_visible()

        page.goto(
            f"{settings.web_base_url}/dashboard/mezonlar",
            wait_until="commit",
        )
        expect(page.get_by_role("heading", name="Критерии", exact=True)).to_be_visible(
            timeout=20_000
        )
        description_input = page.locator("textarea").first
        expect(description_input).to_be_visible(timeout=20_000)
        description_input.fill(company_description)
        description_card = description_input.locator(
            "xpath=ancestor::div[contains(@class, 'MuiCard-root')]"
        )
        with page.expect_response(
            lambda response: response.request.method == "PUT"
            and urlsplit(response.url).path
            == f"/v1/users/{rop_id}/company-description"
        ) as description_info:
            description_card.get_by_role(
                "button", name="Сохранить", exact=True
            ).click()
        assert description_info.value.status == 200

        page.reload(wait_until="commit")
        expect(page.locator("textarea").first).to_have_value(
            company_description,
            timeout=20_000,
        )
        page.goto(
            f"{settings.web_base_url}/dashboard/dynamic-form",
            wait_until="commit",
        )
        expect(page.get_by_text(status_hint, exact=True)).to_be_visible(timeout=20_000)
        expect(page.get_by_text(field_hint, exact=True)).to_be_visible(timeout=20_000)
    finally:
        restore_failures: list[str] = []
        restore_status = rop_request.patch(
            f"/v1/amocrm/statuses/{status_id}/hint",
            data={"hint": str(status.get("hint") or ""), "priority": status_priority},
        )
        if restore_status.status != 200:
            restore_failures.append("status")
        restore_field = rop_request.patch(
            f"/v1/amocrm/fields/{field_id}/hint",
            data={
                "hint": str(field.get("hint") or ""),
                "required": field_required,
            },
        )
        if restore_field.status != 200:
            restore_failures.append("field")
        restore_description = rop_request.put(
            f"/v1/users/{rop_id}/company-description",
            data={"description": original_description},
        )
        if restore_description.status != 200:
            restore_failures.append("company_description")
        assert not restore_failures, (
            "[UAT-ROP-004 cleanup] не восстановлены значения: "
            f"{restore_failures}."
        )


def _uat_rop_005(request: pytest.FixtureRequest) -> None:
    page: Page = request.getfixturevalue("authorized_page_factory")("rop")
    settings: Settings = request.getfixturevalue("test_settings")
    rop_request = request.getfixturevalue("rop_api_request")
    settings_body = _api_json(
        rop_request.get("/v1/calling/settings"),
        checkpoint="[UAT-ROP-005] исходные критерии",
    )
    original = settings_body.get("stored")
    assert isinstance(original, dict)
    changed = {
        "work_start": "08:01",
        "work_end": "19:01",
        "retry_interval_min": 181,
        "max_attempts": 5,
        "before_arrival_min": 61,
        "chala_delay_min": 31,
        "default_call_time": "11:01",
        "bugun_transition_time": "00:01",
    }
    try:
        page.goto(
            f"{settings.web_base_url}/dashboard/mezonlar",
            wait_until="commit",
        )
        expect(page.get_by_role("heading", name="Критерии", exact=True)).to_be_visible(
            timeout=20_000
        )
        criteria_card = page.locator(".MuiCard-root").first
        criteria_inputs = criteria_card.locator("input")
        expect(criteria_inputs).to_have_count(8)
        for index, value in enumerate(changed.values()):
            criteria_inputs.nth(index).fill(str(value))
        with page.expect_response(
            lambda response: response.request.method == "PUT"
            and urlsplit(response.url).path == "/v1/calling/settings"
        ) as saved_info:
            criteria_card.get_by_role("button", name="Сохранить", exact=True).click()
        assert saved_info.value.status == 200
        expect(page.get_by_text("Критерии сохранены", exact=True)).to_be_visible()

        page.reload(wait_until="commit")
        expect(page.get_by_role("heading", name="Критерии", exact=True)).to_be_visible(
            timeout=20_000
        )
        reloaded_inputs = page.locator(".MuiCard-root").first.locator("input")
        expect(reloaded_inputs).to_have_count(8)
        for index, value in enumerate(changed.values()):
            expect(reloaded_inputs.nth(index)).to_have_value(str(value))
        persisted = _api_json(
            rop_request.get("/v1/calling/settings"),
            checkpoint="[UAT-ROP-005] сохранённые критерии",
        )
        assert persisted.get("stored") == changed
    finally:
        restored = rop_request.put("/v1/calling/settings", data=original)
        assert restored.status == 200, (
            "[UAT-ROP-005 cleanup] не удалось восстановить критерии очереди."
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
    "UAT-LND-002": _uat_lnd_002,
    "UAT-SA-001": _uat_sa_001,
    "UAT-SA-002": _uat_sa_002,
    "UAT-SA-003": _uat_sa_003,
    "UAT-SA-004": _uat_sa_004,
    "UAT-SA-005": _uat_sa_005,
    "UAT-SA-006": _uat_sa_006,
    "UAT-ROP-001": _uat_rop_001,
    "UAT-ROP-002": _uat_rop_002,
    "UAT-ROP-003": _uat_rop_003,
    "UAT-ROP-004": _uat_rop_004,
    "UAT-ROP-005": _uat_rop_005,
    "UAT-ROP-006": _uat_rop_006,
    "UAT-OP-001": _uat_op_001,
    "UAT-OP-002": _uat_op_002,
    "UAT-OP-004": _uat_op_004,
    "UAT-OP-007": _uat_op_007,
    "UAT-OP-008": _uat_op_008,
    "UAT-OP-009": _uat_op_009,
    "UAT-FLOW-001": _uat_flow_001,
    "UAT-FLOW-002": _uat_flow_002,
    "UAT-FLOW-003": _uat_flow_003,
}


GATES: dict[str, str] = {}


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
