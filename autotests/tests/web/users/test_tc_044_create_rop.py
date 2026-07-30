from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from playwright.sync_api import APIResponse, Page, expect

from autotests.api.user_api import UserApi
from autotests.config import Settings
from autotests.pages.rop_list_page import RopListPage
from autotests.support.login_rate_guard import LoginRateGuard


AuthorizedPageFactory = Callable[[str], Page]


def _cleanup_rops_by_username(
    superadmin_api: UserApi,
    username: str,
) -> None:
    response = superadmin_api.list_users_by_username(username)
    assert response.status == 200, (
        "[TC-044 cleanup] при поиске тестового РОП ожидали 200, получили "
        f"{response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"[TC-044 cleanup] ожидали JSON-объект списка, получили {body!r}"
    )
    items = body.get("items")
    assert isinstance(items, list), (
        f"[TC-044 cleanup] ожидали массив items, получили {body!r}"
    )

    for item in items:
        assert isinstance(item, dict), (
            f"[TC-044 cleanup] ожидали объект пользователя, получили {item!r}"
        )
        user_id = item.get("id")
        assert isinstance(user_id, str) and user_id, (
            f"[TC-044 cleanup] у пользователя нет id: {item!r}"
        )
        delete_response = superadmin_api.delete_user(user_id)
        assert delete_response.status == 200, (
            "[TC-044 cleanup] при удалении тестового РОП ожидали 200, "
            f"получили {delete_response.status}: {delete_response.text()}"
        )
        delete_body = delete_response.json()
        assert delete_body.get("message") == "o'chirildi", (
            "[TC-044 cleanup] ожидали message=\"o'chirildi\", получили "
            f"{delete_body!r}"
        )


@pytest.mark.web
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.positive
@pytest.mark.serial
def test_tc_044_superadmin_creates_active_rop_who_can_login(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> None:
    """TC-044 — супер-админ создаёт активного РОП с рабочим входом."""
    if (
        not test_settings.superadmin_username
        or not test_settings.superadmin_password
    ):
        pytest.skip(
            "TC-044 требует OPERATOR_AI_SUPERADMIN_USERNAME и "
            "OPERATOR_AI_SUPERADMIN_PASSWORD в локальном .env"
        )

    unique_id = uuid4().hex
    username = f"AT-ROP-{unique_id[:8]}"
    password = f"AT!{unique_id[:12]}"
    first_name = f"Auto{unique_id[:5]}"
    last_name = f"Rop{unique_id[5:10]}"
    phone = f"+99893{uuid4().int % 10_000_000:07d}"
    company_name = f"AT Company {uuid4().hex[:8]}"
    tariff = "taxlil_dashboard"

    page = authorized_page_factory("superadmin")
    superadmin_api = UserApi.from_authorized_page(
        page,
        test_settings.web_base_url,
        discovery_path=RopListPage.PATH,
    )
    rop_list = RopListPage(page)

    try:
        expect(
            rop_list.heading,
            "[TC-044] ожидали список компаний РОП",
        ).to_be_visible()
        expect(
            rop_list.new_rop_button,
            "[TC-044] ожидали кнопку «Новый РОП»",
        ).to_be_visible()

        dialog = rop_list.open_create_dialog()
        expect(
            dialog.dialog,
            "[TC-044] ожидали форму создания РОП",
        ).to_be_visible()
        dialog.fill(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            username=username,
            company_name=company_name,
        )
        dialog.select_tariff("Аналитика")
        expect(
            dialog.create_button,
            "[TC-044] заполненная форма должна разрешать создание",
        ).to_be_enabled()

        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and urlsplit(response.url).path == "/v1/rops"
            )
        ) as create_response_info:
            dialog.create()

        create_response = create_response_info.value
        assert create_response.status == 200, (
            "[TC-044] при создании РОП ожидали 200, получили "
            f"{create_response.status}: {create_response.text()}"
        )
        created = create_response.json()
        assert isinstance(created, dict), (
            f"[TC-044] ожидали JSON-объект РОП, получили {created!r}"
        )
        created_id = created.get("id")
        assert isinstance(created_id, str) and created_id, (
            f"[TC-044] у созданного РОП нет id: {created!r}"
        )
        assert created.get("username") == username, (
            f"[TC-044] сервер создал другого пользователя: {created!r}"
        )
        assert created.get("role") == "rop", (
            f"[TC-044] ожидали role='rop', получили {created!r}"
        )
        assert created.get("company_name") == company_name, (
            f"[TC-044] сохранилась другая компания: {created!r}"
        )
        request_payload = create_response.request.post_data_json
        assert isinstance(request_payload, dict), (
            f"[TC-044] ожидали JSON-тело POST /v1/rops: {request_payload!r}"
        )
        assert request_payload.get("tariff") == tariff, (
            f"[TC-044] frontend отправил другой тариф: {request_payload!r}"
        )

        expect(
            rop_list.success_alert,
            "[TC-044] ожидали уведомление «Пользователь создан»",
        ).to_be_visible()
        created_row = rop_list.row_by_company(company_name)
        expect(
            created_row,
            "[TC-044] новая компания должна появиться в таблице",
        ).to_have_count(1)
        expect(created_row).to_contain_text(username)
        expect(created_row).to_contain_text("Активен")

        list_response = superadmin_api.list_users_by_username(username)
        assert list_response.status == 200, (
            "[TC-044] при контрольном поиске ожидали 200, получили "
            f"{list_response.status}: {list_response.text()}"
        )
        list_body = list_response.json()
        assert isinstance(list_body, dict), (
            f"[TC-044] ожидали JSON-объект списка, получили {list_body!r}"
        )
        items = list_body.get("items")
        assert isinstance(items, list) and len(items) == 1, (
            "[TC-044] ожидали ровно одного РОП с новым username, получили "
            f"{items!r}"
        )
        assert items[0].get("id") == created_id, (
            f"[TC-044] в списке найден другой РОП: {items!r}"
        )
        assert items[0].get("role") == "rop", (
            f"[TC-044] в списке сохранилась другая роль: {items!r}"
        )
        assert items[0].get("is_active") is True, (
            f"[TC-044] новый РОП должен быть активен: {items!r}"
        )
        assert items[0].get("company_name") == company_name, (
            f"[TC-044] в списке сохранилась другая компания: {items!r}"
        )

        login_rate_guard.before_attempt()
        login_response: APIResponse = superadmin_api.login(
            username,
            password,
        )
        assert login_response.status == 200, (
            "[TC-044] созданный РОП должен входить: ожидали 200, получили "
            f"{login_response.status}: {login_response.text()}"
        )
        login_body = login_response.json()
        assert isinstance(login_body, dict), (
            f"[TC-044] ожидали JSON-объект входа, получили {login_body!r}"
        )
        login_user = login_body.get("user")
        assert isinstance(login_user, dict), (
            f"[TC-044] ожидали объект user при входе, получили {login_body!r}"
        )
        assert login_user.get("id") == created_id, (
            f"[TC-044] вошёл другой пользователь: {login_user!r}"
        )
        assert login_user.get("role") == "rop", (
            f"[TC-044] при входе ожидали роль ROP: {login_user!r}"
        )
        access_token = login_body.get("access_token")
        assert isinstance(access_token, str) and access_token, (
            "[TC-044] успешный вход должен вернуть непустой access_token"
        )
    finally:
        _cleanup_rops_by_username(superadmin_api, username)
