from __future__ import annotations

from collections.abc import Callable

import pytest
from playwright.sync_api import Locator, Page, expect

from autotests.config import Settings
from autotests.pages.operator_list_page import OperatorListPage


AuthorizedPageFactory = Callable[[str], Page]

STANDARD_VIEWPORTS = (
    pytest.param({"width": 1280, "height": 720}, id="1280x720"),
    pytest.param({"width": 1366, "height": 768}, id="1366x768"),
    pytest.param({"width": 1920, "height": 1080}, id="1920x1080"),
)
ZOOM_200_VIEWPORT = {"width": 683, "height": 384}


def _assert_in_viewport(
    page: Page,
    locator: Locator,
    *,
    checkpoint: str,
) -> None:
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    viewport = page.viewport_size
    assert box is not None and viewport is not None, (
        f"{checkpoint} элемент или viewport недоступны"
    )
    assert box["x"] >= -1 and box["x"] + box["width"] <= viewport["width"] + 1, (
        f"{checkpoint} элемент выходит за viewport по горизонтали: "
        f"box={box!r}, viewport={viewport!r}"
    )
    assert box["y"] >= -1 and box["y"] + box["height"] <= viewport["height"] + 1, (
        f"{checkpoint} элемент недоступен по вертикали после прокрутки: "
        f"box={box!r}, viewport={viewport!r}"
    )


def _assert_document_has_no_horizontal_overflow(
    page: Page,
    *,
    checkpoint: str,
) -> None:
    widths = page.evaluate(
        """() => ({
            clientWidth: document.documentElement.clientWidth,
            scrollWidth: document.documentElement.scrollWidth
        })"""
    )
    assert isinstance(widths, dict)
    client_width = widths.get("clientWidth")
    scroll_width = widths.get("scrollWidth")
    assert isinstance(client_width, int) and isinstance(scroll_width, int)
    assert scroll_width <= client_width + 1, (
        f"{checkpoint} страница имеет горизонтальный overflow: "
        f"clientWidth={client_width}, scrollWidth={scroll_width}"
    )


def _check_operator_list_and_dialog(
    page: Page,
    settings: Settings,
    *,
    checkpoint: str,
) -> None:
    operator_list = OperatorListPage(page)
    operator_list.open(settings.web_base_url)

    expect(
        operator_list.heading,
        f"{checkpoint} ожидали заголовок списка операторов",
    ).to_be_visible()
    expect(
        operator_list.new_operator_button,
        f"{checkpoint} кнопка создания должна быть доступна",
    ).to_be_visible()
    _assert_in_viewport(
        page,
        operator_list.new_operator_button,
        checkpoint=f"{checkpoint} кнопка «Новый оператор»",
    )
    _assert_document_has_no_horizontal_overflow(
        page,
        checkpoint=f"{checkpoint} список операторов",
    )

    dialog = operator_list.open_create_dialog()
    expect(
        dialog.dialog,
        f"{checkpoint} ожидали форму создания оператора",
    ).to_be_visible()
    _assert_in_viewport(
        page,
        dialog.dialog,
        checkpoint=f"{checkpoint} границы модального окна",
    )
    _assert_in_viewport(
        page,
        dialog.first_name_input,
        checkpoint=f"{checkpoint} первое поле формы",
    )
    _assert_in_viewport(
        page,
        dialog.cancel_button,
        checkpoint=f"{checkpoint} кнопка отмены",
    )
    _assert_in_viewport(
        page,
        dialog.create_button,
        checkpoint=f"{checkpoint} кнопка создания",
    )

    page.keyboard.press("Escape")
    expect(
        dialog.dialog,
        f"{checkpoint} Escape должен закрыть форму без отправки",
    ).to_have_count(0)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.parametrize("viewport", STANDARD_VIEWPORTS)
def test_tc_377_operator_list_and_dialog_fit_standard_viewports(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
    viewport: dict[str, int],
) -> None:
    """TC-377 — список и форма доступны на типовых экранах."""
    page = authorized_page_factory("rop")
    page.set_viewport_size(viewport)

    _check_operator_list_and_dialog(
        page,
        test_settings,
        checkpoint=f"[TC-377:{viewport['width']}x{viewport['height']}]",
    )


@pytest.mark.web
@pytest.mark.high
@pytest.mark.positive
def test_tc_377_operator_dialog_remains_usable_at_200_percent_equivalent(
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """
    TC-377 — эквивалент 1366×768 при масштабе 200% остаётся рабочим.

    Browser zoom в headless Chromium моделируется CSS-viewport 683×384.
    После возврата к 1366×768 раскладка проверяется повторно.
    """
    page = authorized_page_factory("rop")
    page.set_viewport_size(ZOOM_200_VIEWPORT)

    _check_operator_list_and_dialog(
        page,
        test_settings,
        checkpoint="[TC-377:1366x768@200% equivalent]",
    )

    restored_viewport = {"width": 1366, "height": 768}
    page.set_viewport_size(restored_viewport)
    page.reload(wait_until="domcontentloaded")
    operator_list = OperatorListPage(page)
    expect(
        operator_list.heading,
        "[TC-377:restored] после возврата масштаба список должен работать",
    ).to_be_visible()
    _assert_document_has_no_horizontal_overflow(
        page,
        checkpoint="[TC-377:restored] список операторов",
    )
