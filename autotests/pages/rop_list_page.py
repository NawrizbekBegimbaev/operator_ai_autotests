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
        self.deleted_alert = page.get_by_role("alert").filter(
            has_text="Пользователь удалён"
        )
        self.saved_alert = page.get_by_role("alert").filter(
            has_text="Пользователь сохранён"
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

    def open_delete_dialog(self, company_name: str) -> RopDeleteDialog:
        row = self.row_by_company(company_name)
        row.get_by_role("button").last.click()
        return RopDeleteDialog(self.page)

    def open_edit_dialog(self, company_name: str) -> RopEditDialog:
        row = self.row_by_company(company_name)
        actions_cell = row.get_by_role("cell").last
        actions_cell.get_by_role("button").first.click()
        return RopEditDialog(self.page)

    def toggle_active(self, company_name: str) -> None:
        row = self.row_by_company(company_name)
        actions_cell = row.get_by_role("cell").last
        actions_cell.get_by_role("button").nth(2).click()

    def open_amocrm_dialog(
        self,
        company_name: str,
        *,
        user_full_name: str,
    ) -> AmoCrmConnectDialog:
        row = self.row_by_company(company_name)
        amocrm_cell = row.get_by_role("cell").nth(2)
        amocrm_cell.get_by_role("button").click()
        return AmoCrmConnectDialog(
            self.page,
            user_full_name=user_full_name,
        )

    def open_onlinepbx_dialog(
        self,
        company_name: str,
        *,
        user_full_name: str,
    ) -> OnlinePbxConnectDialog:
        row = self.row_by_company(company_name)
        onlinepbx_cell = row.get_by_role("cell").nth(3)
        onlinepbx_cell.get_by_role("button").click()
        return OnlinePbxConnectDialog(
            self.page,
            user_full_name=user_full_name,
        )


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


class RopDeleteDialog:
    def __init__(self, page: Page) -> None:
        self.dialog = page.get_by_role(
            "dialog",
            name="Удалить пользователя",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )
        self.delete_button = self.dialog.get_by_role(
            "button",
            name="Удалить",
            exact=True,
        )

    def cancel(self) -> None:
        self.cancel_button.click()

    def confirm(self) -> None:
        self.delete_button.click()


class RopEditDialog:
    def __init__(self, page: Page) -> None:
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
        self.phone_input = self.dialog.get_by_label("Телефон", exact=True)
        self.role_input = self.dialog.get_by_label("Роль", exact=True)
        self.company_name_input = self.dialog.get_by_label(
            "Название компании",
            exact=True,
        )
        self.save_button = self.dialog.get_by_role(
            "button",
            name="Сохранить",
            exact=True,
        )

    def fill(
        self,
        *,
        first_name: str,
        last_name: str,
        phone_subscriber: str,
        company_name: str,
    ) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.phone_input.fill(phone_subscriber)
        self.company_name_input.fill(company_name)

    def save(self) -> None:
        self.save_button.click()


class AmoCrmConnectDialog:
    def __init__(self, page: Page, *, user_full_name: str) -> None:
        self.dialog = page.get_by_role(
            "dialog",
            name=f"Подключение AmoCRM: {user_full_name}",
            exact=True,
        )
        self.domain_input = self.dialog.get_by_label("Domain", exact=True)
        self.client_id_input = self.dialog.get_by_label(
            "Client ID",
            exact=True,
        )
        self.client_secret_input = self.dialog.get_by_label(
            "Client secret",
            exact=True,
        )
        self.redirect_uri_input = self.dialog.get_by_label(
            "Redirect URI",
            exact=True,
        )
        self.access_token_input = self.dialog.get_by_label(
            "Access token",
            exact=True,
        )
        self.lead_source_input = self.dialog.get_by_label(
            "Lead source",
            exact=True,
        )
        self.connect_button = self.dialog.get_by_role(
            "button",
            name="Подключить",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )


class OnlinePbxConnectDialog:
    def __init__(self, page: Page, *, user_full_name: str) -> None:
        self.dialog = page.get_by_role(
            "dialog",
            name=f"Подключение OnlinePBX: {user_full_name}",
            exact=True,
        )
        self.domain_input = self.dialog.get_by_label("Domain", exact=True)
        self.api_key_input = self.dialog.get_by_label(
            "API key",
            exact=True,
        )
        self.connect_button = self.dialog.get_by_role(
            "button",
            name="Подключить",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )
