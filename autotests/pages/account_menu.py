from __future__ import annotations

from playwright.sync_api import Page


class AccountMenu:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.account_button = page.get_by_role(
            "button",
            name="Account button",
            exact=True,
        )
        self.logout_button = page.get_by_role(
            "button",
            name="Выйти",
            exact=True,
        )
        self.change_password_button = page.get_by_role(
            "button",
            name="Сменить пароль",
            exact=True,
        )

    def open(self) -> None:
        self.account_button.click()

    def logout(self) -> None:
        self.logout_button.click()

    def open_change_password(self) -> None:
        self.change_password_button.click()

    def go_back(self) -> None:
        self.page.go_back()

    def reload(self) -> None:
        self.page.reload()
