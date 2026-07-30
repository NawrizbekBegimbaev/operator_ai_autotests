from __future__ import annotations

import re
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Locator, Page, Request, expect

from autotests.config import Settings
from autotests.pages.login_page import LoginPage
from autotests.pages.operator_list_page import (
    OperatorCreateDialog,
    OperatorListPage,
)
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.temporary_users import OperatorDraft


def _is_focused(locator: Locator) -> bool:
    return bool(
        locator.evaluate(
            "element => element === element.ownerDocument.activeElement"
        )
    )


def _tab_to(
    page: Page,
    locator: Locator,
    *,
    checkpoint: str,
    max_presses: int = 60,
) -> None:
    for _ in range(max_presses + 1):
        if _is_focused(locator):
            expect(locator, f"{checkpoint} ожидали keyboard focus").to_be_focused()
            assert locator.evaluate(
                "element => element.matches(':focus-visible')"
            ), f"{checkpoint} элемент в keyboard focus не имеет :focus-visible"
            return
        page.keyboard.press("Tab")

    active = page.evaluate(
        """() => {
            const element = document.activeElement;
            return {
                tag: element?.tagName ?? null,
                role: element?.getAttribute?.('role') ?? null,
                ariaLabel: element?.getAttribute?.('aria-label') ?? null
            };
        }"""
    )
    raise AssertionError(
        f"{checkpoint} элемент не достигнут за {max_presses} Tab; "
        f"активный элемент={active!r}"
    )


def _type_with_keyboard(
    page: Page,
    locator: Locator,
    value: str,
    *,
    checkpoint: str,
) -> None:
    _tab_to(page, locator, checkpoint=checkpoint)
    page.keyboard.type(value)
    expect(
        locator,
        f"{checkpoint} ожидали введённое с клавиатуры значение",
    ).to_have_value(value)


def _select_first_enabled_option_with_keyboard(
    page: Page,
    dialog: OperatorCreateDialog,
) -> None:
    _tab_to(
        page,
        dialog.extension_select,
        checkpoint="[TC-378] PBX select",
    )
    page.keyboard.press("ArrowDown")
    options = page.get_by_role("option")
    expect(
        options.first,
        "[TC-378] PBX options должны открыться с клавиатуры",
    ).to_be_visible()

    option_count = options.count()
    assert option_count > 0, "[TC-378] список PBX options пуст"
    for _ in range(option_count + 1):
        active_option = page.locator('[role="option"]:focus')
        if active_option.count() == 1:
            is_disabled = active_option.get_attribute("aria-disabled") == "true"
            if not is_disabled:
                page.keyboard.press("Enter")
                expect(options.first).not_to_be_visible()
                selected_text = dialog.extension_select.text_content().strip()
                assert selected_text, (
                    "[TC-378] выбор PBX с клавиатуры не установил значение"
                )
                return
        page.keyboard.press("ArrowDown")

    raise AssertionError(
        "[TC-378] не удалось выбрать доступный PBX option клавиатурой"
    )


def _assert_focus_inside_dialog(dialog: OperatorCreateDialog) -> None:
    assert dialog.dialog.evaluate(
        "element => element.contains(element.ownerDocument.activeElement)"
    ), "[TC-378] focus вышел за пределы открытого модального окна"


@pytest.mark.web
@pytest.mark.medium
@pytest.mark.positive
@pytest.mark.auth
def test_tc_378_critical_path_is_keyboard_accessible(
    clean_login_page: Page,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
    operator_draft: OperatorDraft,
) -> None:
    """
    TC-378 — вход, навигация и форма доступны без мыши.

    Форма заполняется достаточно для проверки select/date и фокуса, но не
    отправляется. Закрытие Escape дополнительно подтверждает отсутствие POST.
    """
    page = clean_login_page
    login_page = LoginPage(page)
    credentials = test_settings.credentials_for("rop")
    create_requests: list[Request] = []

    def remember_create_request(request: Request) -> None:
        if (
            request.method == "POST"
            and urlsplit(request.url).path == "/v1/operators"
        ):
            create_requests.append(request)

    page.on("request", remember_create_request)
    login_page.open(test_settings.web_base_url)

    _type_with_keyboard(
        page,
        login_page.username_input,
        credentials.username,
        checkpoint="[TC-378] поле логина",
    )
    _type_with_keyboard(
        page,
        login_page.password_input,
        credentials.password,
        checkpoint="[TC-378] поле пароля",
    )
    _tab_to(
        page,
        login_page.show_password_button,
        checkpoint="[TC-378] кнопка показа пароля",
    )
    page.keyboard.press("Enter")
    expect(login_page.password_input).to_have_attribute("type", "text")
    page.keyboard.press("Enter")
    expect(login_page.password_input).to_have_attribute("type", "password")

    _tab_to(
        page,
        login_page.submit_button,
        checkpoint="[TC-378] кнопка входа",
    )
    login_rate_guard.before_attempt()
    page.keyboard.press("Enter")
    expect(
        page,
        "[TC-378] Enter на кнопке входа должен авторизовать РОП",
    ).to_have_url(f"{test_settings.web_base_url}/dashboard/dynamic-form")

    queue_link = page.get_by_role(
        "link",
        name="Настройка очереди",
        exact=True,
    )
    _tab_to(
        page,
        queue_link,
        checkpoint="[TC-378] ссылка «Настройка очереди»",
    )
    page.keyboard.press("Enter")
    expect(page).to_have_url(
        f"{test_settings.web_base_url}/dashboard/operator-pipelines"
    )
    expect(
        page.get_by_role(
            "heading",
            name="Настройка очереди",
            exact=True,
        )
    ).to_be_visible()

    operators_link = page.get_by_role(
        "link",
        name="Операторы",
        exact=True,
    )
    _tab_to(
        page,
        operators_link,
        checkpoint="[TC-378] ссылка «Операторы»",
    )
    page.keyboard.press("Enter")
    expect(page).to_have_url(
        f"{test_settings.web_base_url}/dashboard/operators"
    )

    operator_list = OperatorListPage(page)
    expect(operator_list.heading).to_be_visible()
    _tab_to(
        page,
        operator_list.new_operator_button,
        checkpoint="[TC-378] кнопка «Новый оператор»",
    )
    page.keyboard.press("Enter")
    dialog = OperatorCreateDialog(page)
    expect(dialog.dialog).to_be_visible()

    _type_with_keyboard(
        page,
        dialog.first_name_input,
        operator_draft.first_name,
        checkpoint="[TC-378] Имя",
    )
    _type_with_keyboard(
        page,
        dialog.last_name_input,
        operator_draft.last_name,
        checkpoint="[TC-378] Фамилия",
    )
    local_phone = operator_draft.phone.removeprefix("+998")
    _tab_to(
        page,
        dialog.phone_input,
        checkpoint="[TC-378] Телефон",
    )
    page.keyboard.type(local_phone)
    actual_phone_digits = re.sub(r"\D", "", dialog.phone_input.input_value())
    assert actual_phone_digits == local_phone, (
        "[TC-378] телефонная маска должна сохранить девять введённых "
        f"цифр; ожидали {local_phone!r}, получили {actual_phone_digits!r}"
    )
    _type_with_keyboard(
        page,
        dialog.password_input,
        operator_draft.password,
        checkpoint="[TC-378] Пароль оператора",
    )

    show_operator_password = dialog.dialog.get_by_role(
        "button",
        name="Показать пароль",
        exact=True,
    )
    _tab_to(
        page,
        show_operator_password,
        checkpoint="[TC-378] глазок пароля оператора",
    )
    page.keyboard.press("Enter")
    expect(dialog.password_input).to_have_attribute("type", "text")
    page.keyboard.press("Enter")
    expect(dialog.password_input).to_have_attribute("type", "password")

    _type_with_keyboard(
        page,
        dialog.username_input,
        operator_draft.username,
        checkpoint="[TC-378] Имя пользователя",
    )
    _select_first_enabled_option_with_keyboard(page, dialog)
    _type_with_keyboard(
        page,
        dialog.salary_input,
        str(operator_draft.salary),
        checkpoint="[TC-378] Зарплата",
    )

    _tab_to(
        page,
        dialog.salary_day_input,
        checkpoint="[TC-378] День зарплаты",
    )
    month, day, year = (
        operator_draft.salary_day[5:7],
        operator_draft.salary_day[8:10],
        operator_draft.salary_day[0:4],
    )
    # Chromium обрабатывает сегменты native date-input как MMDDYYYY,
    # независимо от локализованного визуального формата.
    page.keyboard.type(f"{month}{day}{year}")
    expect(
        dialog.salary_day_input,
        "[TC-378] дата должна вводиться с клавиатуры",
    ).to_have_value(operator_draft.salary_day)

    _tab_to(
        page,
        dialog.create_button,
        checkpoint="[TC-378] кнопка «Создать»",
        max_presses=5,
    )
    expect(
        dialog.create_button,
        "[TC-378] валидная форма должна сделать submit доступным",
    ).to_be_enabled()
    _assert_focus_inside_dialog(dialog)

    page.keyboard.press("Shift+Tab")
    expect(
        dialog.cancel_button,
        "[TC-378] Shift+Tab должен вернуть focus на «Отмена»",
    ).to_be_focused()
    _assert_focus_inside_dialog(dialog)

    page.keyboard.press("Escape")
    expect(
        dialog.dialog,
        "[TC-378] Escape должен закрыть модальное окно",
    ).to_have_count(0)
    expect(
        operator_list.new_operator_button,
        "[TC-378] после Escape focus должен вернуться на trigger",
    ).to_be_focused()
    assert not create_requests, (
        "[TC-378] клавиатурная проверка не должна отправлять POST /v1/operators"
    )
