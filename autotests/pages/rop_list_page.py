from __future__ import annotations

import re

from playwright.sync_api import Locator, Page


class RopListPage:
    PATH = "/dashboard/rop"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name=re.compile(r"^Компании РОП · \d+$"),
        )
        self.companies_table = page.get_by_role("table")
        self.new_rop_button = page.get_by_role(
            "button",
            name="Новый РОП",
            exact=True,
        )
        self.success_alert = page.get_by_role("alert").filter(
            has_text="Пользователь создан"
        )
        self.rop_menu_link = page.get_by_role("link", name="РОПы", exact=True)
        self.leads_menu_link = page.get_by_role("link", name="Лиды", exact=True)
        self.tariffs_menu_link = page.get_by_role("link", name="Тарифы", exact=True)

    def row_by_company(self, company_name: str) -> Locator:
        return self.companies_table.get_by_role("row").filter(
            has_text=company_name
        )

    def open_create_dialog(self) -> RopCreateDialog:
        self.new_rop_button.click()
        return RopCreateDialog(self.page)


class RopCreateDialog:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role(
            "dialog",
            name="Создать РОП",
            exact=True,
        )
        self.first_name_input = self.dialog.get_by_label("Имя", exact=True)
        self.last_name_input = self.dialog.get_by_label("Фамилия", exact=True)
        self.phone_input = self.dialog.get_by_label("Телефон", exact=True)
        self.password_input = self.dialog.get_by_label("Пароль", exact=True)
        self.username_input = self.dialog.get_by_label(
            "Имя пользователя (логин)",
            exact=True,
        )
        self.company_name_input = self.dialog.get_by_label(
            "Название компании",
            exact=True,
        )
        self.tariff_select = self.dialog.get_by_role(
            "combobox",
            name="Тариф",
            exact=True,
        )
        self.create_button = self.dialog.get_by_role(
            "button",
            name="Создать",
            exact=True,
        )

    def fill(
        self,
        *,
        first_name: str,
        last_name: str,
        phone: str,
        password: str,
        username: str,
        company_name: str,
    ) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.phone_input.fill(phone)
        self.password_input.fill(password)
        self.username_input.fill(username)
        self.company_name_input.fill(company_name)

    def select_tariff(self, option_name: str) -> None:
        self.tariff_select.click()
        self.page.get_by_role(
            "option",
            name=option_name,
            exact=True,
        ).click()

    def create(self) -> None:
        self.create_button.click()
