from __future__ import annotations

import os
import re
from collections.abc import Callable, Generator
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

import pytest
from playwright.sync_api import (
    APIRequestContext,
    Browser,
    BrowserContext,
    Page,
    expect,
)
from playwright.sync_api import Playwright

from autotests.config import ConfigurationError, Settings
from autotests.pages.login_page import LoginPage
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.auth_requests import login, require_access_token
from autotests.support.tenant_isolation import (
    CrossTenantContext,
    TenantActor,
)
from autotests.support.temporary_users import OperatorDraft, TemporaryOperator


StorageState = dict[str, Any]
RoleStorageStateProvider = Callable[[str], StorageState]
AuthorizedPageFactory = Callable[[str], Page]
RoleApiTokenProvider = Callable[[str], str]

ROLE_START_PATHS = {
    "superadmin": "/dashboard/rop",
    "rop": "/dashboard/dynamic-form",
    "operator": "/dashboard/home",
}


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    try:
        return Settings.from_env()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.fixture(scope="session")
def api_base_url(test_settings: Settings) -> str:
    try:
        return test_settings.require_api_base_url()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.fixture(scope="session")
def login_rate_guard() -> LoginRateGuard:
    return LoginRateGuard()


@pytest.fixture(scope="session")
def role_api_token(
    playwright: Playwright,
    api_base_url: str,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> RoleApiTokenProvider:
    """Ленивый session-кэш API-токена для каждой роли под lock."""
    cached_tokens: dict[str, str] = {}
    cache_lock = Lock()

    def get_api_token(role: str) -> str:
        with cache_lock:
            if role in cached_tokens:
                return cached_tokens[role]

            username, password = _credentials_for_role(
                test_settings,
                role,
            )
            request_context = playwright.request.new_context(
                base_url=api_base_url,
            )
            try:
                login_rate_guard.before_attempt()
                response = request_context.post(
                    "/v1/auth/login",
                    data={
                        "username": username,
                        "password": password,
                    },
                )
                actual_status = response.status
                response_text = response.text()
                body = response.json()
            finally:
                request_context.dispose()

            assert actual_status == 200, (
                f"[api_token:{role}] ожидали 200 при служебном входе, "
                f"получили {actual_status}: {response_text}"
            )
            assert isinstance(body, dict), (
                f"[api_token:{role}] ожидали JSON-объект входа, "
                f"получили {body!r}"
            )
            user = body.get("user")
            assert isinstance(user, dict), (
                f"[api_token:{role}] ожидали объект user, "
                f"получили {user!r}: {body!r}"
            )
            expected_api_role = {
                "superadmin": "super_admin",
                "rop": "rop",
                "operator": "operator",
            }[role]
            assert user.get("role") == expected_api_role, (
                f"[api_token:{role}] ожидали role={expected_api_role!r}, "
                f"получили {user.get('role')!r}: {user!r}"
            )
            access_token = body.get("access_token")
            assert isinstance(access_token, str) and access_token, (
                f"[api_token:{role}] ожидали непустой access_token: "
                f"{body!r}"
            )
            cached_tokens[role] = access_token
            return cached_tokens[role]

    return get_api_token


@pytest.fixture(scope="session")
def rop_api_request(
    playwright: Playwright,
    api_base_url: str,
    role_api_token: RoleApiTokenProvider,
) -> Generator[APIRequestContext, None, None]:
    request_context = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers={
            "Authorization": f"Bearer {role_api_token('rop')}",
            "Content-Type": "application/json",
        },
    )
    try:
        yield request_context
    finally:
        request_context.dispose()


def _json_object(
    response: Any,
    *,
    checkpoint: str,
    expected_status: int = 200,
) -> dict[str, Any]:
    assert response.status == expected_status, (
        f"{checkpoint} ожидали HTTP {expected_status}, получили "
        f"{response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"{checkpoint} ожидали JSON-объект, получили {body!r}"
    )
    return body


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def cross_tenant_context(
    playwright: Playwright,
    api_base_url: str,
    role_api_token: RoleApiTokenProvider,
    login_rate_guard: LoginRateGuard,
) -> Generator[CrossTenantContext, None, None]:
    """
    Подготавливает межклиентскую проверку без постоянного второго РОП.

    Текущий staging-РОП используется только для чтения как компания Б.
    Компания А создаётся временно, получает одного временного оператора
    и полностью удаляется после pytest-сессии.
    """
    superadmin_token = role_api_token("superadmin")
    source_rop_token = role_api_token("rop")
    superadmin_request = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers=_auth_headers(superadmin_token),
    )
    source_rop_request = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers=_auth_headers(source_rop_token),
    )
    anonymous_request = playwright.request.new_context(
        base_url=api_base_url,
        extra_http_headers={"Content-Type": "application/json"},
    )
    outsider_rop_request: APIRequestContext | None = None
    outsider_operator_request: APIRequestContext | None = None
    created_rop: dict[str, Any] | None = None
    created_operator: dict[str, Any] | None = None

    try:
        source_rop = _json_object(
            source_rop_request.get("/v1/auth/me"),
            checkpoint="[cross_tenant setup] текущий РОП",
        )
        assert source_rop.get("role") == "rop", (
            "[cross_tenant setup] источник данных должен иметь role='rop', "
            f"получили {source_rop!r}"
        )
        source_operators_page = _json_object(
            source_rop_request.get(
                "/v1/users",
                params={
                    "filter": "role='operator'",
                    "page": 1,
                    "perPage": 100,
                },
            ),
            checkpoint="[cross_tenant setup] операторы текущего РОП",
        )
        source_operators = source_operators_page.get("items")
        assert isinstance(source_operators, list) and source_operators, (
            "[cross_tenant setup] у текущего РОП должен быть хотя бы один "
            "оператор для положительного контроля межклиентской изоляции."
        )
        source_operator = source_operators[0]
        assert isinstance(source_operator, dict), (
            "[cross_tenant setup] ожидали объект оператора, получили "
            f"{source_operator!r}"
        )

        rop_unique_id = uuid4().hex
        rop_username = f"AT-X-{rop_unique_id[:8]}"
        rop_password = f"AT!X{rop_unique_id[:12]}"
        created_rop = _json_object(
            superadmin_request.post(
                "/v1/rops",
                data={
                    "username": rop_username,
                    "password": rop_password,
                    "first_name": "AT-Outsider",
                    "last_name": "Tenant",
                    "phone": f"+99890{uuid4().int % 10_000_000:07d}",
                    "company_name": f"AT-X-{uuid4().hex[:8]}",
                    "tariff": "taxlil_dashboard",
                },
            ),
            checkpoint="[cross_tenant setup] временный РОП",
        )
        assert created_rop.get("role") == "rop", (
            "[cross_tenant setup] ожидали временного role='rop', получили "
            f"{created_rop!r}"
        )

        outsider_rop_login = login(
            anonymous_request,
            login_rate_guard,
            username=rop_username,
            password=rop_password,
        )
        outsider_rop_token, outsider_rop_user = require_access_token(
            outsider_rop_login,
            checkpoint="[cross_tenant setup] вход временного РОП",
        )
        assert outsider_rop_user.get("id") == created_rop.get("id"), (
            "[cross_tenant setup] после входа получили не временного РОП: "
            f"{outsider_rop_user!r}"
        )
        outsider_rop_request = playwright.request.new_context(
            base_url=api_base_url,
            extra_http_headers=_auth_headers(outsider_rop_token),
        )

        operator_unique_id = uuid4().hex
        operator_username = f"AT-X-{operator_unique_id[:8]}"
        operator_password = f"AT!X{operator_unique_id[:12]}"
        created_operator = _json_object(
            outsider_rop_request.post(
                "/v1/operators",
                data={
                    "username": operator_username,
                    "password": operator_password,
                    "first_name": "AT-Outsider",
                    "last_name": "Operator",
                    "phone": f"+99890{uuid4().int % 10_000_000:07d}",
                    "pbx_extension": f"ATX{operator_unique_id[:6]}",
                    "salary": 1,
                    "salary_day": date.today().isoformat(),
                },
            ),
            checkpoint="[cross_tenant setup] временный оператор",
        )
        assert created_operator.get("role") == "operator", (
            "[cross_tenant setup] ожидали временного role='operator', "
            f"получили {created_operator!r}"
        )
        assert created_operator.get("company_id") == created_rop.get("id"), (
            "[cross_tenant setup] временный оператор принадлежит не своей "
            f"компании: {created_operator!r}"
        )

        outsider_operator_login = login(
            anonymous_request,
            login_rate_guard,
            username=operator_username,
            password=operator_password,
        )
        outsider_operator_token, outsider_operator_user = (
            require_access_token(
                outsider_operator_login,
                checkpoint="[cross_tenant setup] вход временного оператора",
            )
        )
        assert outsider_operator_user.get("id") == created_operator.get("id"), (
            "[cross_tenant setup] после входа получили не временного "
            f"оператора: {outsider_operator_user!r}"
        )
        outsider_operator_request = playwright.request.new_context(
            base_url=api_base_url,
            extra_http_headers=_auth_headers(outsider_operator_token),
        )

        yield CrossTenantContext(
            source=TenantActor(
                rop=source_rop,
                operator=source_operator,
                rop_token=source_rop_token,
            ),
            outsider=TenantActor(
                rop=created_rop,
                operator=created_operator,
                rop_token=outsider_rop_token,
                operator_token=outsider_operator_token,
            ),
            source_rop_request=source_rop_request,
            outsider_rop_request=outsider_rop_request,
            outsider_operator_request=outsider_operator_request,
        )
    finally:
        if outsider_rop_request is not None and created_operator is not None:
            operator_id = created_operator.get("id")
            if isinstance(operator_id, str) and operator_id:
                response = outsider_rop_request.delete(
                    f"/v1/users/{operator_id}"
                )
                assert response.status == 200, (
                    "[cross_tenant teardown] при удалении временного "
                    f"оператора ожидали 200, получили {response.status}: "
                    f"{response.text()}"
                )
        if created_rop is not None:
            rop_id = created_rop.get("id")
            if isinstance(rop_id, str) and rop_id:
                response = superadmin_request.delete(f"/v1/users/{rop_id}")
                assert response.status == 200, (
                    "[cross_tenant teardown] при удалении временного РОП "
                    f"ожидали 200, получили {response.status}: "
                    f"{response.text()}"
                )

        if outsider_operator_request is not None:
            outsider_operator_request.dispose()
        if outsider_rop_request is not None:
            outsider_rop_request.dispose()
        anonymous_request.dispose()
        source_rop_request.dispose()
        superadmin_request.dispose()


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, object],
) -> dict[str, object]:
    return {
        **browser_context_args,
        "locale": "ru-RU",
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def clean_login_page(page: Page) -> Generator[Page, None, None]:
    """Новая неавторизованная страница для тестов самого входа."""
    page.context.clear_cookies()
    yield page


def _credentials_for_role(settings: Settings, role: str) -> tuple[str, str]:
    credentials = settings.credentials_for(role)
    return credentials.username, credentials.password


@pytest.fixture(scope="session")
def role_storage_state(
    browser: Browser,
    browser_context_args: dict[str, object],
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> RoleStorageStateProvider:
    """Ленивый session-кэш авторизованного состояния для каждой роли."""
    cached_states: dict[str, StorageState] = {}
    cache_lock = Lock()

    def get_storage_state(role: str) -> StorageState:
        if role not in ROLE_START_PATHS:
            raise pytest.UsageError(f"Неизвестная роль для UI-сессии: {role!r}.")

        with cache_lock:
            if role in cached_states:
                return cached_states[role]

            username, password = _credentials_for_role(test_settings, role)
            context = browser.new_context(**browser_context_args)
            try:
                page = context.new_page()
                login_page = LoginPage(page)

                login_page.open(test_settings.web_base_url)
                login_rate_guard.before_attempt()
                login_page.sign_in(username=username, password=password)
                expected_url = (
                    f"{test_settings.web_base_url}{ROLE_START_PATHS[role]}"
                )
                expect(
                    page,
                    f"[storage_state:{role}] после служебного входа ожидали "
                    f"точный адрес {expected_url}",
                ).to_have_url(expected_url)

                cached_states[role] = context.storage_state()
                return cached_states[role]
            finally:
                context.close()

    return get_storage_state


@pytest.fixture
def operator_draft() -> OperatorDraft:
    unique_id = uuid4().hex
    return OperatorDraft(
        username=f"AT-{unique_id[:10]}",
        password=f"AT!{unique_id[:12]}",
        first_name=f"Auto{unique_id[:5]}",
        last_name=f"Operator{unique_id[5:10]}",
        phone=f"+99890{uuid4().int % 10_000_000:07d}",
        pbx_extension=f"AT{unique_id[:6]}",
        salary=1,
        salary_day=date.today().isoformat(),
    )


@pytest.fixture
def temporary_operator(
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> Generator[TemporaryOperator, None, None]:
    """Создаёт отдельного оператора на staging и всегда удаляет его."""
    create_response = rop_api_request.post(
        "/v1/operators",
        data=operator_draft.api_payload(),
    )
    assert create_response.status == 200, (
        "[temporary_operator setup] при создании оператора ожидали 200, "
        f"получили {create_response.status}: {create_response.text()}"
    )
    created = create_response.json()
    assert isinstance(created, dict), (
        "[temporary_operator setup] ожидали JSON-объект оператора, "
        f"получили {created!r}"
    )
    operator_id = created.get("id")
    assert isinstance(operator_id, str) and operator_id, (
        "[temporary_operator setup] ожидали непустой id оператора, "
        f"получили {created!r}"
    )
    assert created.get("username") == operator_draft.username, (
        "[temporary_operator setup] сервер вернул другого пользователя: "
        f"ожидали username={operator_draft.username!r}, получили {created!r}"
    )
    assert created.get("role") == "operator", (
        "[temporary_operator setup] ожидали role='operator', "
        f"получили {created!r}"
    )

    operator = TemporaryOperator(
        id=operator_id,
        username=operator_draft.username,
        password=operator_draft.password,
        first_name=operator_draft.first_name,
        last_name=operator_draft.last_name,
        phone=operator_draft.phone,
        pbx_extension=operator_draft.pbx_extension,
        salary=operator_draft.salary,
        salary_day=operator_draft.salary_day,
        rop_request=rop_api_request,
    )

    try:
        yield operator
    finally:
        delete_response = rop_api_request.delete(f"/v1/users/{operator_id}")
        assert delete_response.status == 200, (
            "[temporary_operator teardown] при удалении оператора "
            f"ожидали 200, получили {delete_response.status}: "
            f"{delete_response.text()}"
        )
        delete_body = delete_response.json()
        assert delete_body.get("message") == "o'chirildi", (
            "[temporary_operator teardown] ожидали "
            f"message=\"o'chirildi\", получили {delete_body!r}"
        )


def _artifact_directory(node_id: str) -> Path:
    safe_node_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", node_id).strip("-")
    root = Path(os.getenv("OPERATOR_AI_ARTIFACT_DIR", "test-results"))
    return root / safe_node_id


@pytest.fixture
def authorized_page_factory(
    browser: Browser,
    browser_context_args: dict[str, object],
    request: pytest.FixtureRequest,
    role_storage_state: RoleStorageStateProvider,
) -> Generator[AuthorizedPageFactory, None, None]:
    """
    Для каждого теста создаёт новый контекст из session storage_state роли.

    Trace и screenshot сохраняются только при падении теста.
    """
    opened_contexts: list[tuple[BrowserContext, Page]] = []

    def create_authorized_page(role: str) -> Page:
        context = browser.new_context(
            **browser_context_args,
            storage_state=role_storage_state(role),
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        opened_contexts.append((context, page))
        return page

    yield create_authorized_page

    call_report = getattr(request.node, "rep_call", None)
    test_failed = bool(call_report and call_report.failed)
    artifact_directory = _artifact_directory(request.node.nodeid)

    for context, page in opened_contexts:
        if test_failed:
            artifact_directory.mkdir(parents=True, exist_ok=True)
            if not page.is_closed():
                page.screenshot(
                    path=artifact_directory / "test-failed-1.png",
                    full_page=True,
                )
            context.tracing.stop(path=artifact_directory / "trace.zip")
        else:
            context.tracing.stop()
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Добавляет UAT-ID в JUnit properties до выполнения теста/skip."""
    seen_uat_ids: set[str] = set()
    for item in items:
        marker = item.get_closest_marker("uat_id")
        if marker is None:
            continue
        if len(marker.args) != 1 or not isinstance(marker.args[0], str):
            raise pytest.UsageError(
                f"Некорректный @pytest.mark.uat_id у {item.nodeid}."
            )
        case_id = marker.args[0]
        if case_id in seen_uat_ids:
            raise pytest.UsageError(
                f"UAT-ID {case_id} связан более чем с одним pytest-item."
            )
        seen_uat_ids.add(case_id)
        item.user_properties.append(("uat_id", case_id))
