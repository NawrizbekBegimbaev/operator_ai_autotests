from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import (
    APIRequestContext,
    Page,
    Playwright,
    Request,
    expect,
)

from autotests.config import Settings
from autotests.pages.operator_list_page import OperatorListPage
from autotests.support.auth_requests import login, require_access_token
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.operator_api import (
    cleanup_users_by_username,
    list_extensions,
    list_users_by_username,
)
from autotests.support.temporary_users import OperatorDraft


AuthorizedPageFactory = Callable[[str], Page]


def _free_extension(rop_request: APIRequestContext, checkpoint: str) -> str:
    extensions = list_extensions(rop_request, checkpoint=checkpoint)
    free = [
        item
        for item in extensions
        if item.get("enabled") is True and item.get("assigned") is False
    ]
    assert free, f"{checkpoint} на staging нет свободного включённого номера"
    extension = free[0].get("extension")
    assert isinstance(extension, str) and extension, (
        f"{checkpoint} у свободного extension нет номера: {free[0]!r}"
    )
    return extension


def _open_create_dialog(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> tuple[Page, OperatorListPage]:
    page = authorized_page_factory("rop")
    operator_list = OperatorListPage(page)
    operator_list.open(test_settings.web_base_url)
    expect(
        operator_list.new_operator_button,
        "[operator-create setup] ожидали кнопку «Новый оператор»",
    ).to_be_visible()
    return page, operator_list


@pytest.mark.web
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.serial
def test_tc_052_rop_creates_operator_with_free_extension(
    authorized_page_factory: AuthorizedPageFactory,
    playwright: Playwright,
    api_base_url: str,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-052 — РОП создаёт оператора со свободным OnlinePBX-номером."""
    extension = _free_extension(rop_api_request, "[TC-052 setup]")
    draft = replace(operator_draft, pbx_extension=extension, salary=1_000_000)
    page, operator_list = _open_create_dialog(
        authorized_page_factory,
        test_settings,
    )

    try:
        dialog = operator_list.open_create_dialog()
        expect(
            dialog.dialog,
            "[TC-052] ожидали открытую форму создания оператора",
        ).to_be_visible()
        dialog.fill_personal_data(draft)
        dialog.select_extension(extension)
        expect(
            dialog.create_button,
            "[TC-052] полностью заполненная форма должна разрешать создание",
        ).to_be_enabled()

        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and urlsplit(response.url).path == "/v1/operators"
            )
        ) as create_response_info:
            dialog.create()

        create_response = create_response_info.value
        assert create_response.status == 200, (
            "[TC-052] при создании оператора ожидали 200, получили "
            f"{create_response.status}: {create_response.text()}"
        )
        created = create_response.json()
        assert isinstance(created, dict), (
            f"[TC-052] ожидали JSON-объект оператора, получили {created!r}"
        )
        assert created.get("username") == draft.username, (
            "[TC-052] сервер создал другого пользователя: "
            f"{created!r}"
        )
        assert created.get("role") == "operator", (
            f"[TC-052] ожидали role='operator', получили {created!r}"
        )
        assert created.get("pbx_extension") == extension, (
            "[TC-052] ожидали выбранный внутренний номер "
            f"{extension!r}, получили {created!r}"
        )
        expect(
            operator_list.success_alert,
            "[TC-052] ожидали уведомление «Пользователь создан»",
        ).to_be_visible()
        expect(
            operator_list.row_by_full_name(draft.first_name, draft.last_name),
            "[TC-052] ожидали новую строку оператора в таблице",
        ).to_have_count(1)

        users = list_users_by_username(
            rop_api_request,
            draft.username,
            checkpoint="[TC-052] проверка списка API",
        )
        assert len(users) == 1, (
            f"[TC-052] ожидали одного оператора, получили {users!r}"
        )
        assert users[0].get("is_active") is True, (
            f"[TC-052] новый оператор должен быть активен: {users[0]!r}"
        )
        assert users[0].get("pbx_extension") == extension, (
            f"[TC-052] в API сохранился другой extension: {users[0]!r}"
        )

        public_request = playwright.request.new_context(base_url=api_base_url)
        try:
            operator_login = login(
                public_request,
                login_rate_guard,
                username=draft.username,
                password=draft.password,
            )
            _, login_user = require_access_token(
                operator_login,
                checkpoint="[TC-052] вход созданного оператора",
            )
            assert login_user.get("id") == users[0].get("id"), (
                "[TC-052] после создания вошёл другой оператор: "
                f"{login_user!r}"
            )
        finally:
            public_request.dispose()
    finally:
        cleanup_users_by_username(
            rop_api_request,
            draft.username,
            checkpoint="[TC-052 cleanup]",
        )


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.xfail(
    reason=(
        "BUG-023: занятый PBX extension остаётся доступным для выбора "
        "в форме создания оператора"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tc_054_busy_extension_is_disabled(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-054 — занятый внутренний номер виден, но выбрать его нельзя."""
    extensions = list_extensions(
        rop_api_request,
        checkpoint="[TC-054 setup]",
    )
    busy = [
        item
        for item in extensions
        if item.get("enabled") is True and item.get("assigned") is True
    ]
    assert busy, "[TC-054 setup] на staging нет занятого включённого номера"
    busy_extension = busy[0].get("extension")
    assert isinstance(busy_extension, str) and busy_extension

    _, operator_list = _open_create_dialog(
        authorized_page_factory,
        test_settings,
    )
    dialog = operator_list.open_create_dialog()
    expect(dialog.dialog).to_be_visible()
    dialog.open_extension_options()
    busy_option = dialog.extension_option(busy_extension)
    expect(
        busy_option,
        f"[TC-054] ожидали занятый номер {busy_extension!r} в списке",
    ).to_be_visible()
    expect(
        busy_option,
        f"[TC-054] занятый номер {busy_extension!r} должен быть недоступен",
    ).to_be_disabled()


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.serial
def test_tc_063_double_create_sends_one_request_and_creates_one_operator(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-063 — двойной клик создаёт ровно одного оператора."""
    extension = _free_extension(rop_api_request, "[TC-063 setup]")
    draft = replace(operator_draft, pbx_extension=extension, salary=1_000_000)
    page, operator_list = _open_create_dialog(
        authorized_page_factory,
        test_settings,
    )
    create_requests: list[Request] = []

    def remember_create_request(request: Request) -> None:
        if (
            request.method == "POST"
            and urlsplit(request.url).path == "/v1/operators"
        ):
            create_requests.append(request)

    page.on("request", remember_create_request)

    try:
        dialog = operator_list.open_create_dialog()
        expect(dialog.dialog).to_be_visible()
        dialog.fill_personal_data(draft)
        dialog.select_extension(extension)
        expect(dialog.create_button).to_be_enabled()

        dialog.create_button.dblclick(delay=20)
        expect(
            operator_list.success_alert,
            "[TC-063] ожидали одно успешное создание",
        ).to_be_visible()

        users = list_users_by_username(
            rop_api_request,
            draft.username,
            checkpoint="[TC-063] проверка результата",
        )
        assert len(create_requests) == 1, (
            "[TC-063] двойной клик должен отправить один POST /v1/operators, "
            f"получили {len(create_requests)}"
        )
        assert len(users) == 1, (
            "[TC-063] после двойного клика должен существовать один оператор, "
            f"получили {users!r}"
        )
    finally:
        cleanup_users_by_username(
            rop_api_request,
            draft.username,
            checkpoint="[TC-063 cleanup]",
        )
