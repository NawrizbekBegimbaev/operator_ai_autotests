from __future__ import annotations

from collections.abc import Callable, Generator
from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from playwright.sync_api import APIResponse, Page

from autotests.api.user_api import UserApi
from autotests.config import Settings


AuthorizedPageFactory = Callable[[str], Page]


def _response_text(response: APIResponse) -> str:
    return response.text()


@pytest.fixture
def tc031_test_operator(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> Generator[dict[str, Any], None, None]:
    unique_id = uuid4().hex
    username = f"AT-{unique_id[:8]}"
    phone_suffix = uuid4().int % 10_000_000
    rop_page = authorized_page_factory("rop")
    rop_api = UserApi.from_authorized_page(
        rop_page,
        test_settings.web_base_url,
        discovery_path="/dashboard/operators",
    )
    create_response = rop_api.create_operator(
        {
            "username": username,
            "password": f"AT!{unique_id[:12]}",
            "first_name": username,
            "last_name": "TC-031",
            "phone": f"+99890{phone_suffix:07d}",
            "pbx_extension": f"AT{unique_id[:6]}",
            "salary": 1,
            "salary_day": date.today().isoformat(),
        }
    )
    assert create_response.status == 200, (
        "[TC-031 setup] при создании уникального оператора ожидали 200, "
        f"получили {create_response.status}: {_response_text(create_response)}"
    )
    created_operator = create_response.json()
    assert isinstance(created_operator, dict), (
        "[TC-031 setup] ожидали JSON-объект созданного оператора, "
        f"получили {created_operator!r}"
    )
    assert created_operator.get("username") == username, (
        "[TC-031 setup] ожидали созданного оператора с username "
        f"{username!r}, получили {created_operator!r}"
    )
    assert created_operator.get("role") == "operator", (
        "[TC-031 setup] ожидали роль 'operator', получили "
        f"{created_operator.get('role')!r}: {created_operator!r}"
    )
    operator_id = created_operator.get("id")
    assert isinstance(operator_id, str) and operator_id, (
        "[TC-031 setup] ожидали непустой строковый id оператора, "
        f"получили {operator_id!r}: {created_operator!r}"
    )

    yield created_operator

    delete_response = rop_api.delete_user(operator_id)
    assert delete_response.status == 200, (
        "[TC-031 teardown] при удалении тестового оператора ожидали 200, "
        f"получили {delete_response.status}: {_response_text(delete_response)}"
    )
    delete_body = delete_response.json()
    assert delete_body.get("message") == "o'chirildi", (
        "[TC-031 teardown] ожидали message=\"o'chirildi\", получили "
        f"{delete_body!r}"
    )


@pytest.mark.api
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.xfail(
    reason=(
        "BUG-021: super-admin может изменить оператора РОП через "
        "PATCH /v1/users/{id}"
    ),
    strict=True,
)
def test_tc_031_superadmin_cannot_patch_rop_operator(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    tc031_test_operator: dict[str, Any],
) -> None:
    """
    TC-031 — super-admin не может менять оператора, принадлежащего РОП.

    Ожидаемый результат: PATCH оператора от super-admin возвращает 403 с
    detail `ruxsat yo'q`; все данные оператора остаются без изменений.
    """
    superadmin_page = authorized_page_factory("superadmin")
    user_api = UserApi.from_authorized_page(
        superadmin_page,
        test_settings.web_base_url,
        discovery_path="/dashboard/rop",
    )
    operator_id = tc031_test_operator["id"]

    before_response = user_api.get_user(operator_id)
    assert before_response.status == 200, (
        "[TC-031] перед проверкой запрета ожидали GET оператора 200, "
        f"получили {before_response.status}: "
        f"{_response_text(before_response)}"
    )
    operator_before = before_response.json()
    assert isinstance(operator_before, dict), (
        "[TC-031] перед PATCH ожидали JSON-объект оператора, "
        f"получили {operator_before!r}"
    )
    assert operator_before.get("username") == tc031_test_operator["username"], (
        "[TC-031] перед PATCH получили не того тестового оператора: "
        f"ожидали username={tc031_test_operator['username']!r}, "
        f"получили {operator_before!r}"
    )

    patch_response = user_api.patch_user(
        operator_id,
        {"first_name": f"AT-CHG-{uuid4().hex[:8]}"},
    )
    after_response = user_api.get_user(operator_id)
    assert after_response.status == 200, (
        "[TC-031] после запрещённого PATCH ожидали GET оператора 200, "
        f"получили {after_response.status}: {_response_text(after_response)}"
    )
    operator_after = after_response.json()
    assert isinstance(operator_after, dict), (
        "[TC-031] после PATCH ожидали JSON-объект оператора, "
        f"получили {operator_after!r}"
    )

    assert patch_response.status == 403, (
        "[TC-031] super-admin не должен менять оператора РОП: ожидали "
        f"PATCH 403, получили {patch_response.status}: "
        f"{_response_text(patch_response)}; данные до={operator_before!r}, "
        f"после={operator_after!r}"
    )
    patch_body = patch_response.json()
    assert patch_body.get("status") == 403, (
        "[TC-031] в теле отказа ожидали status=403, получили "
        f"{patch_body.get('status')!r}: {patch_body!r}"
    )
    assert patch_body.get("title") == "Forbidden", (
        "[TC-031] в теле отказа ожидали title='Forbidden', получили "
        f"{patch_body.get('title')!r}: {patch_body!r}"
    )
    assert patch_body.get("detail") == "ruxsat yo'q", (
        "[TC-031] в теле отказа ожидали detail=\"ruxsat yo'q\", получили "
        f"{patch_body.get('detail')!r}: {patch_body!r}"
    )
    assert operator_after == operator_before, (
        "[TC-031] после запрещённого PATCH данные оператора изменились: "
        f"до={operator_before!r}, после={operator_after!r}"
    )
