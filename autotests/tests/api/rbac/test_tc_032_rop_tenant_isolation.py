from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from playwright.sync_api import APIResponse, Page

from autotests.api.user_api import UserApi
from autotests.config import Settings


AuthorizedPageFactory = Callable[[str], Page]


@dataclass(frozen=True)
class RopTenant:
    rop: dict[str, Any]
    operator: dict[str, Any]
    api: UserApi


def _response_text(response: APIResponse) -> str:
    return response.text()


def _unique_phone() -> str:
    subscriber_suffix = uuid4().int % 10_000_000
    return f"+99890{subscriber_suffix:07d}"


def _assert_created_user(
    response: APIResponse,
    *,
    case_phase: str,
    expected_username: str,
    expected_role: str,
) -> dict[str, Any]:
    assert response.status == 200, (
        f"[TC-032 {case_phase}] при создании {expected_role} ожидали 200, "
        f"получили {response.status}: {_response_text(response)}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"[TC-032 {case_phase}] ожидали JSON-объект созданного пользователя, "
        f"получили {body!r}"
    )
    assert body.get("username") == expected_username, (
        f"[TC-032 {case_phase}] ожидали username={expected_username!r}, "
        f"получили {body!r}"
    )
    assert body.get("role") == expected_role, (
        f"[TC-032 {case_phase}] ожидали role={expected_role!r}, "
        f"получили {body.get('role')!r}: {body!r}"
    )
    user_id = body.get("id")
    assert isinstance(user_id, str) and user_id, (
        f"[TC-032 {case_phase}] ожидали непустой строковый id, "
        f"получили {user_id!r}: {body!r}"
    )
    return body


def _login_as_generated_rop(
    bootstrap_api: UserApi,
    *,
    username: str,
    password: str,
    expected_rop_id: str,
) -> str:
    response = bootstrap_api.login(username, password)
    assert response.status == 200, (
        "[TC-032 setup] при входе созданного РОП ожидали 200, "
        f"получили {response.status}: {_response_text(response)}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        "[TC-032 setup] при входе РОП ожидали JSON-объект, "
        f"получили {body!r}"
    )
    user = body.get("user")
    assert isinstance(user, dict), (
        "[TC-032 setup] в ответе входа ожидали объект user, "
        f"получили {user!r}: {body!r}"
    )
    assert user.get("id") == expected_rop_id, (
        "[TC-032 setup] после входа получили не того РОП: "
        f"ожидали id={expected_rop_id!r}, получили {user!r}"
    )
    assert user.get("username") == username, (
        "[TC-032 setup] после входа ожидали username "
        f"{username!r}, получили {user!r}"
    )
    assert user.get("role") == "rop", (
        "[TC-032 setup] после входа ожидали role='rop', "
        f"получили {user.get('role')!r}: {user!r}"
    )
    access_token = body.get("access_token")
    assert isinstance(access_token, str) and access_token, (
        "[TC-032 setup] после входа РОП ожидали непустой access_token."
    )
    return access_token


@pytest.fixture
def tc032_tenants(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> Generator[tuple[RopTenant, RopTenant], None, None]:
    superadmin_page = authorized_page_factory("superadmin")
    superadmin_api = UserApi.from_authorized_page(
        superadmin_page,
        test_settings.web_base_url,
        discovery_path="/dashboard/rop",
    )
    created_rops: list[dict[str, Any]] = []
    created_operators: list[tuple[UserApi, dict[str, Any]]] = []
    tenants: list[RopTenant] = []

    try:
        for tenant_label in ("A", "B"):
            unique_id = uuid4().hex
            rop_username = f"AT-{unique_id[:8]}"
            rop_password = f"AT!{unique_id[:12]}"
            rop_response = superadmin_api.create_rop(
                {
                    "username": rop_username,
                    "password": rop_password,
                    "first_name": f"AT-{tenant_label}",
                    "last_name": "TC-032",
                    "phone": _unique_phone(),
                    "company_name": f"AT-{uuid4().hex[:8]}",
                    "tariff": "taxlil_dashboard",
                }
            )
            rop = _assert_created_user(
                rop_response,
                case_phase="setup",
                expected_username=rop_username,
                expected_role="rop",
            )
            created_rops.append(rop)

            rop_access_token = _login_as_generated_rop(
                superadmin_api,
                username=rop_username,
                password=rop_password,
                expected_rop_id=rop["id"],
            )
            rop_api = UserApi(
                page=superadmin_page,
                api_base_url=superadmin_api.api_base_url,
                access_token=rop_access_token,
            )

            operator_unique_id = uuid4().hex
            operator_username = f"AT-{operator_unique_id[:8]}"
            operator_response = rop_api.create_operator(
                {
                    "username": operator_username,
                    "password": f"AT!{operator_unique_id[:12]}",
                    "first_name": f"AT-{tenant_label}",
                    "last_name": "Operator-TC-032",
                    "phone": _unique_phone(),
                    "pbx_extension": f"AT{operator_unique_id[:6]}",
                    "salary": 1,
                    "salary_day": date.today().isoformat(),
                }
            )
            operator = _assert_created_user(
                operator_response,
                case_phase="setup",
                expected_username=operator_username,
                expected_role="operator",
            )
            assert operator.get("company_id") == rop["id"], (
                "[TC-032 setup] созданный оператор должен принадлежать "
                f"своему РОП {rop['id']!r}, получили {operator!r}"
            )
            created_operators.append((rop_api, operator))
            tenants.append(
                RopTenant(
                    rop=rop,
                    operator=operator,
                    api=rop_api,
                )
            )

        assert len(tenants) == 2, (
            "[TC-032 setup] ожидали подготовить два тестовых РОП, "
            f"получили {len(tenants)}"
        )
        yield tenants[0], tenants[1]
    finally:
        for rop_api, operator in reversed(created_operators):
            delete_operator = rop_api.delete_user(operator["id"])
            assert delete_operator.status == 200, (
                "[TC-032 teardown] при удалении оператора ожидали 200, "
                f"получили {delete_operator.status}: "
                f"{_response_text(delete_operator)}"
            )
            delete_operator_body = delete_operator.json()
            assert delete_operator_body.get("message") == "o'chirildi", (
                "[TC-032 teardown] при удалении оператора ожидали "
                f"message=\"o'chirildi\", получили {delete_operator_body!r}"
            )

        for rop in reversed(created_rops):
            delete_rop = superadmin_api.delete_user(rop["id"])
            assert delete_rop.status == 200, (
                "[TC-032 teardown] при удалении РОП ожидали 200, "
                f"получили {delete_rop.status}: {_response_text(delete_rop)}"
            )
            delete_rop_body = delete_rop.json()
            assert delete_rop_body.get("message") == "o'chirildi", (
                "[TC-032 teardown] при удалении РОП ожидали "
                f"message=\"o'chirildi\", получили {delete_rop_body!r}"
            )


def _operator_items_for_tenant(tenant: RopTenant) -> list[dict[str, Any]]:
    response = tenant.api.list_users(
        filter_expression="role='operator'",
        per_page=100,
    )
    assert response.status == 200, (
        "[TC-032] при чтении операторов РОП ожидали 200, "
        f"получили {response.status}: {_response_text(response)}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        "[TC-032] в списке операторов ожидали JSON-объект, "
        f"получили {body!r}"
    )
    assert body.get("page") == 1, (
        "[TC-032] в списке операторов ожидали page=1, "
        f"получили {body.get('page')!r}: {body!r}"
    )
    assert body.get("perPage") == 100, (
        "[TC-032] в списке операторов ожидали perPage=100, "
        f"получили {body.get('perPage')!r}: {body!r}"
    )
    assert body.get("totalPages") == 1, (
        "[TC-032] у нового РОП с одним оператором ожидали totalPages=1, "
        f"получили {body.get('totalPages')!r}: {body!r}"
    )
    assert body.get("totalItems") == 1, (
        "[TC-032] у нового РОП ожидали totalItems=1, "
        f"получили {body.get('totalItems')!r}: {body!r}"
    )
    items = body.get("items")
    assert isinstance(items, list), (
        "[TC-032] в ответе ожидали массив items, "
        f"получили {items!r}: {body!r}"
    )
    assert len(items) == 1, (
        "[TC-032] у нового РОП ожидали ровно одного оператора, "
        f"получили {len(items)}: {items!r}"
    )
    assert all(isinstance(item, dict) for item in items), (
        "[TC-032] в items ожидали только JSON-объекты, "
        f"получили {items!r}"
    )
    return items


@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
def test_tc_032_each_rop_sees_only_own_operator(
    tc032_tenants: tuple[RopTenant, RopTenant],
) -> None:
    """
    TC-032 — РОП-А не видит операторов РОП-Б, и наоборот.

    Ожидаемый результат: каждый РОП получает ровно своего оператора;
    ID, username и company_id чужого оператора в списке отсутствуют.
    """
    tenant_a, tenant_b = tc032_tenants

    operators_a = _operator_items_for_tenant(tenant_a)
    operators_b = _operator_items_for_tenant(tenant_b)

    expected_a = {
        (
            tenant_a.operator["id"],
            tenant_a.operator["username"],
            tenant_a.rop["id"],
        )
    }
    expected_b = {
        (
            tenant_b.operator["id"],
            tenant_b.operator["username"],
            tenant_b.rop["id"],
        )
    }
    actual_a = {
        (item.get("id"), item.get("username"), item.get("company_id"))
        for item in operators_a
    }
    actual_b = {
        (item.get("id"), item.get("username"), item.get("company_id"))
        for item in operators_b
    }

    assert actual_a == expected_a, (
        "[TC-032] РОП-А должен видеть только своего оператора: "
        f"ожидали {expected_a!r}, получили {actual_a!r}"
    )
    assert actual_b == expected_b, (
        "[TC-032] РОП-Б должен видеть только своего оператора: "
        f"ожидали {expected_b!r}, получили {actual_b!r}"
    )
    assert actual_a.isdisjoint(actual_b), (
        "[TC-032] списки операторов РОП-А и РОП-Б пересеклись: "
        f"A={actual_a!r}, B={actual_b!r}"
    )
