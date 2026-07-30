from __future__ import annotations

from playwright.sync_api import Page


class AccountChangePasswordDialog:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role(
            "dialog",
            name="Parolni o'zgartirish",
            exact=True,
        )
        self.old_password_input = self.dialog.get_by_label(
            "Eski parol",
            exact=True,
        )
        self.new_password_input = self.dialog.get_by_label(
            "Yangi parol",
            exact=True,
        )
        self.confirm_password_input = self.dialog.get_by_label(
            "Yangi parolni takrorlang",
            exact=True,
        )
        self.save_button = self.dialog.get_by_role(
            "button",
            name="Saqlash",
            exact=True,
        )
        self.password_mismatch = self.dialog.get_by_text(
            "Parollar mos kelmadi",
            exact=True,
        )
        self.password_too_short = self.dialog.get_by_text(
            "Yangi parol kamida 8 ta belgi bo'lsin",
            exact=True,
        )
        self.success_alert = page.get_by_role("alert").filter(
            has_text="Parol yangilandi"
        )

    def fill(
        self,
        *,
        old_password: str,
        new_password: str,
        confirmation: str,
    ) -> None:
        self.old_password_input.fill(old_password)
        self.new_password_input.fill(new_password)
        self.confirm_password_input.fill(confirmation)

    def save(self) -> None:
        self.save_button.click()
