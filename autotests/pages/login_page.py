from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Page


class LoginPage:
    SIGN_IN_PATH = "/auth/jwt/sign-in"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_input = page.get_by_label("Логин", exact=True)
        self.password_input = page.get_by_label("Пароль", exact=True)
        self.submit_button = page.get_by_role("button", name="Войти", exact=True)
        self.show_password_button = page.get_by_role(
            "button",
            name="показать",
            exact=True,
        )
        self.hide_password_button = page.get_by_role(
            "button",
            name="скрыть",
            exact=True,
        )
        self.error_alert = page.get_by_role("alert")
        # MUI FormHelperText не имеет доступной ARIA-роли. Его ID стабильно
        # формируется от явного ID соответствующего поля.
        self.username_validation = page.locator("#signin-username-helper-text")
        self.password_validation = page.locator("#signin-password-helper-text")

    def open(self, base_url: str) -> None:
        self.page.goto(
            urljoin(f"{base_url}/", self.SIGN_IN_PATH),
            wait_until="commit",
        )

    def sign_in(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit()

    def submit(self) -> None:
        self.submit_button.click()

    def show_password(self) -> None:
        self.show_password_button.click()

    def hide_password(self) -> None:
        self.hide_password_button.click()
