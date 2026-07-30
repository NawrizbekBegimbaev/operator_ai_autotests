from __future__ import annotations

from collections.abc import Callable

import pytest
from playwright.sync_api import Locator, Page, Request, expect

from autotests.config import Settings
from autotests.pages.operator_list_page import OperatorListPage


AuthorizedPageFactory = Callable[[str], Page]


def _blur_empty_field(page: Page, field: Locator) -> None:
    field.click()
    page.keyboard.press("Tab")


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.validation
def test_tc_053_required_operator_fields_block_empty_create(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """
    TC-053 — пустая форма не отправляется.

    Уточнено по факту 30.07.2026: после простого focus/blur отдельная
    подсказка не обязательна для телефона, PBX extension и дня зарплаты.
    """
    page = authorized_page_factory("rop")
    operator_list = OperatorListPage(page)
    operator_list.open(test_settings.web_base_url)
    create_requests: list[Request] = []

    page.on(
        "request",
        lambda request: (
            create_requests.append(request)
            if request.method == "POST" and request.url.endswith("/v1/operators")
            else None
        ),
    )

    expect(
        operator_list.new_operator_button,
        "[TC-053] ожидали кнопку «Новый оператор»",
    ).to_be_visible()
    dialog = operator_list.open_create_dialog()
    expect(
        dialog.dialog,
        "[TC-053] ожидали пустую форму создания оператора",
    ).to_be_visible()

    expect(dialog.first_name_input).to_have_value("")
    expect(dialog.last_name_input).to_have_value("")
    expect(dialog.phone_input).to_have_value("")
    expect(dialog.password_input).to_have_value("")
    expect(dialog.username_input).to_have_value("")
    expect(dialog.salary_input).to_have_value("")
    expect(dialog.salary_day_input).to_have_value("")

    for field in (
        dialog.first_name_input,
        dialog.last_name_input,
        dialog.phone_input,
        dialog.password_input,
        dialog.username_input,
        dialog.extension_select,
        dialog.salary_input,
        dialog.salary_day_input,
    ):
        _blur_empty_field(page, field)

    expected_messages_after_blur = (
        "Имя обязательно",
        "Фамилия обязательна",
        "Пароль должен содержать не менее 8 символов",
        "Имя пользователя обязательно",
        "Зарплата обязательна",
    )
    for message in expected_messages_after_blur:
        expect(
            dialog.dialog.get_by_text(message, exact=True),
            f"[TC-053] после focus/blur ожидали подсказку {message!r}",
        ).to_be_visible()

    expect(
        dialog.create_button,
        "[TC-053] пустая форма не должна разрешать создание",
    ).to_be_disabled()
    dialog.create_button.evaluate("(button) => button.click()")
    page.wait_for_timeout(300)
    assert create_requests == [], (
        "[TC-053] пустая форма не должна отправлять POST /v1/operators, "
        f"получено запросов: {len(create_requests)}"
    )
