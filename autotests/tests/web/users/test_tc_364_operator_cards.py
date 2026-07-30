from __future__ import annotations

from collections.abc import Callable
from itertools import combinations
from typing import Any

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from autotests.config import Settings
from autotests.pages.operator_detail_page import OperatorDetailPage
from autotests.support.operator_api import (
    OperatorApiContractError,
    get_operator,
    list_operators,
)


AuthorizedPageFactory = Callable[[str], Page]


def _display_name(operator: dict[str, Any]) -> str:
    full_name = " ".join(
        str(operator.get(field) or "").strip()
        for field in ("first_name", "last_name")
    ).strip()
    return full_name or str(operator.get("username") or "").strip()


def _two_distinguishable_operators(
    rop_request: APIRequestContext,
) -> tuple[dict[str, Any], dict[str, Any]]:
    operators = list_operators(
        rop_request,
        checkpoint="[TC-364 setup] список операторов",
    )
    for first, second in combinations(operators, 2):
        first_id = first.get("id")
        second_id = second.get("id")
        if not all(
            isinstance(value, str) and value
            for value in (first_id, second_id)
        ):
            raise OperatorApiContractError(
                "[TC-364 setup] у оператора отсутствует строковый id: "
                f"{first!r}, {second!r}"
            )
        if (
            _display_name(first)
            and _display_name(second)
            and _display_name(first) != _display_name(second)
            and first.get("username") != second.get("username")
        ):
            return (
                get_operator(
                    rop_request,
                    str(first_id),
                    checkpoint="[TC-364 setup] первый оператор",
                ),
                get_operator(
                    rop_request,
                    str(second_id),
                    checkpoint="[TC-364 setup] второй оператор",
                ),
            )
    pytest.skip(
        "[TC-364 setup] нужны два оператора с различимыми именами и логинами"
    )


def _verify_profile(
    detail: OperatorDetailPage,
    operator: dict[str, Any],
) -> None:
    operator_id = str(operator["id"])
    full_name = _display_name(operator)
    username = str(operator.get("username") or "").strip()
    phone = str(operator.get("phone") or "").strip()
    extension = str(operator.get("pbx_extension") or "").strip()
    if not all((full_name, username, phone, extension)):
        raise OperatorApiContractError(
            "[TC-364 setup] профиль не содержит обязательные отображаемые "
            f"данные: {operator!r}"
        )

    detail.page.wait_for_url(f"**/dashboard/operators/{operator_id}")
    expect(
        detail.operator_heading(full_name),
        f"[TC-364] ожидали карточку оператора {operator_id}",
    ).to_be_visible()
    expect(detail.profile_text(f"@{username}")).to_be_visible()
    expect(detail.profile_text(phone)).to_be_visible()
    expect(detail.profile_text(f"доб. {extension}")).to_be_visible()
    expect(detail.presence_label).to_be_visible()
    expect(
        detail.account_action(operator.get("is_active") is not False)
    ).to_be_visible()


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
def test_tc_364_cards_keep_selected_operator_identity(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    rop_api_request: APIRequestContext,
) -> None:
    """TC-364 — URL и профиль всегда относятся к выбранному оператору."""
    first, second = _two_distinguishable_operators(rop_api_request)
    page = authorized_page_factory("rop")
    detail = OperatorDetailPage(page)

    detail.open(test_settings.web_base_url, str(first["id"]))
    _verify_profile(detail, first)

    detail.open(test_settings.web_base_url, str(second["id"]))
    _verify_profile(detail, second)
    expect(
        detail.operator_heading(_display_name(first)),
        "[TC-364] имя первого оператора не должно оставаться в заголовке",
    ).to_have_count(0)

    page.reload(wait_until="commit")
    _verify_profile(detail, second)
