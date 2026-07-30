from __future__ import annotations

import re
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page

from autotests.support.temporary_users import OperatorDraft


class OperatorListPage:
    PATH = "/dashboard/operators"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name="Операторы")
        self.new_operator_button = page.get_by_role(
            "button",
            name="Новый оператор",
            exact=True,
        )
        self.table = page.get_by_role("table")
        self.success_alert = page.get_by_role("alert").filter(
            has_text="Пользователь создан"
        )

    def open(self, base_url: str) -> None:
        self.page.goto(
            urljoin(f"{base_url}/", self.PATH.lstrip("/")),
            wait_until="commit",
        )

    def open_create_dialog(self) -> OperatorCreateDialog:
        self.new_operator_button.click()
        return OperatorCreateDialog(self.page)

    def row_by_full_name(self, first_name: str, last_name: str) -> Locator:
        return self.table.get_by_role("row").filter(
            has_text=f"{first_name} {last_name}"
        )

    def open_edit_dialog(
        self,
        first_name: str,
        last_name: str,
    ) -> OperatorEditDialog:
        row = self.row_by_full_name(first_name, last_name)
        row.get_by_role("button").first.click()
        return OperatorEditDialog(self.page)


class OperatorCreateDialog:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role(
            "dialog",
            name="Создать оператора",
            exact=True,
        )
        self.first_name_input = self.dialog.get_by_label("Имя", exact=True)
        self.last_name_input = self.dialog.get_by_label("Фамилия", exact=True)
        self.phone_input = self.dialog.get_by_label("Телефон", exact=True)
        self.password_input = self.dialog.get_by_label("Пароль", exact=True)
        self.username_input = self.dialog.get_by_label(
            "Имя пользователя",
            exact=True,
        )
        self.extension_select = self.dialog.get_by_role(
            "combobox",
            name=re.compile(r"^PBX extension"),
        )
        self.salary_input = self.dialog.get_by_label("Зарплата", exact=True)
        self.salary_day_input = self.dialog.get_by_label(
            "День зарплаты",
            exact=True,
        )
        self.create_button = self.dialog.get_by_role(
            "button",
            name="Создать",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )

    def fill_personal_data(self, draft: OperatorDraft) -> None:
        self.first_name_input.fill(draft.first_name)
        self.last_name_input.fill(draft.last_name)
        self.phone_input.fill(draft.phone)
        self.password_input.fill(draft.password)
        self.username_input.fill(draft.username)
        self.salary_input.fill(str(draft.salary))
        self.salary_day_input.fill(draft.salary_day)

    def open_extension_options(self) -> None:
        self.extension_select.click()

    def extension_option(self, extension: str) -> Locator:
        return self.page.locator(
            f'[role="option"][data-value="{extension}"]'
        )

    def busy_options(self) -> Locator:
        return self.page.get_by_role("option").filter(has_text="занят")

    def select_extension(self, extension: str) -> None:
        self.open_extension_options()
        self.extension_option(extension).click()

    def create(self) -> None:
        self.create_button.click()


class OperatorEditDialog:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role(
            "dialog",
            name="Редактировать пользователя",
            exact=True,
        )
        self.first_name_input = self.dialog.get_by_label("Имя", exact=True)
        self.last_name_input = self.dialog.get_by_label("Фамилия", exact=True)
        self.username_input = self.dialog.get_by_label(
            "Имя пользователя",
            exact=True,
        )
        self.save_button = self.dialog.get_by_role(
            "button",
            name="Сохранить",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )

    def has_visible_loading_indicator(self) -> bool:
        progress = self.dialog.get_by_role("progressbar")
        if progress.count() > 0 and progress.first.is_visible():
            return True

        aria_busy = (
            self.dialog.get_attribute("aria-busy"),
            self.save_button.get_attribute("aria-busy"),
        )
        if "true" in aria_busy:
            return True

        button_text = self.save_button.inner_text().strip()
        return button_text not in {"", "Сохранить"}
