from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import (
    APIRequestContext,
    Locator,
    Page,
    Request,
    expect,
)

from autotests.config import Settings
from autotests.pages.operator_list_page import OperatorListPage
from autotests.support.operator_api import list_extensions
from autotests.support.temporary_users import OperatorDraft


AuthorizedPageFactory = Callable[[str], Page]


def _free_extension(
    rop_api_request: APIRequestContext,
    *,
    checkpoint: str,
) -> str:
    extensions = list_extensions(rop_api_request, checkpoint=checkpoint)
    free_extensions = [
        item
        for item in extensions
        if item.get("enabled") is True and item.get("assigned") is False
    ]
    assert free_extensions, (
        f"{checkpoint} на staging нет свободного включённого PBX extension"
    )
    extension = free_extensions[0].get("extension")
    assert isinstance(extension, str) and extension, (
        f"{checkpoint} у свободного extension нет номера: "
        f"{free_extensions[0]!r}"
    )
    return extension


def _fill_salary_and_blur(
    page: Page,
    salary_input: Locator,
    value: str,
) -> None:
    salary_input.fill(value)
    page.keyboard.press("Tab")


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.boundary
@pytest.mark.validation
def test_tc_056_zero_is_rejected_and_negative_sign_is_filtered(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    operator_draft: OperatorDraft,
    rop_api_request: APIRequestContext,
) -> None:
    """
    TC-056 — 0 отклоняется, знак минус фильтруется.

    Уточнено по факту 30.07.2026: попытка ввести -1 оставляет в поле 1.
    """
    extension = _free_extension(
        rop_api_request,
        checkpoint="[TC-056 setup]",
    )
    page = authorized_page_factory("rop")
    operator_list = OperatorListPage(page)
    operator_list.open(test_settings.web_base_url)
    create_requests: list[Request] = []

    page.on(
        "request",
        lambda request: (
            create_requests.append(request)
            if (
                request.method == "POST"
                and urlsplit(request.url).path == "/v1/operators"
            )
            else None
        ),
    )

    expect(
        operator_list.new_operator_button,
        "[TC-056] ожидали кнопку «Новый оператор»",
    ).to_be_visible(timeout=20_000)
    dialog = operator_list.open_create_dialog()
    expect(
        dialog.dialog,
        "[TC-056] ожидали форму создания оператора",
    ).to_be_visible()
    dialog.fill_personal_data(operator_draft)
    dialog.select_extension(extension)

    salary_error = dialog.dialog.get_by_text(
        "Укажите зарплату",
        exact=True,
    )

    _fill_salary_and_blur(page, dialog.salary_input, "-1")
    expect(
        dialog.salary_input,
        "[TC-056] знак минус не должен сохраняться в поле зарплаты",
    ).to_have_value("1")
    expect(
        salary_error,
        "[TC-056] после фильтрации -1 до 1 ошибка не ожидается",
    ).to_be_hidden()
    expect(
        dialog.create_button,
        "[TC-056] отфильтрованное положительное значение должно приниматься",
    ).to_be_enabled()

    _fill_salary_and_blur(page, dialog.salary_input, "0")
    expect(
        salary_error,
        "[TC-056] для нулевой зарплаты ожидали подсказку",
    ).to_be_visible()
    expect(
        dialog.create_button,
        "[TC-056] нулевая зарплата не должна разрешать создание",
    ).to_be_disabled()

    _fill_salary_and_blur(page, dialog.salary_input, "1000000")
    expect(
        salary_error,
        "[TC-056] положительная зарплата не должна показывать ошибку",
    ).to_be_hidden()
    expect(
        dialog.create_button,
        "[TC-056] корректно заполненная форма должна разрешать создание",
    ).to_be_enabled()

    page.wait_for_timeout(300)
    assert create_requests == [], (
        "[TC-056] проверка границ не должна создавать оператора; "
        f"получено POST /v1/operators: {len(create_requests)}"
    )
