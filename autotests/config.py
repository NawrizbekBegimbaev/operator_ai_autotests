from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TARGET_ENVS = frozenset({"staging", "test"})


class ConfigurationError(RuntimeError):
    """Конфигурация не позволяет безопасно запустить автотесты."""


@dataclass(frozen=True)
class Settings:
    target_env: str
    web_base_url: str
    superadmin_username: str
    superadmin_password: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(PROJECT_ROOT / ".env", override=False)

        required_names = (
            "OPERATOR_AI_TARGET_ENV",
            "OPERATOR_AI_WEB_BASE_URL",
            "OPERATOR_AI_SUPERADMIN_USERNAME",
            "OPERATOR_AI_SUPERADMIN_PASSWORD",
        )
        values = {name: os.getenv(name, "").strip() for name in required_names}
        missing = [name for name, value in values.items() if not value]
        if missing:
            names = ", ".join(missing)
            raise ConfigurationError(
                "Не заданы обязательные переменные окружения: "
                f"{names}. Добавьте их в локальный .env."
            )

        target_env = values["OPERATOR_AI_TARGET_ENV"].lower()
        if target_env not in ALLOWED_TARGET_ENVS:
            allowed = ", ".join(sorted(ALLOWED_TARGET_ENVS))
            raise ConfigurationError(
                "OPERATOR_AI_TARGET_ENV должен явно указывать безопасное окружение "
                f"({allowed}); получено: {target_env!r}."
            )

        configured_web_url = values["OPERATOR_AI_WEB_BASE_URL"]
        parsed_url = urlsplit(configured_web_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ConfigurationError(
                "OPERATOR_AI_WEB_BASE_URL должен быть абсолютным HTTP(S)-адресом."
            )
        web_base_url = urlunsplit(
            (parsed_url.scheme, parsed_url.netloc, "", "", "")
        ).rstrip("/")

        return cls(
            target_env=target_env,
            web_base_url=web_base_url,
            superadmin_username=values["OPERATOR_AI_SUPERADMIN_USERNAME"],
            superadmin_password=values["OPERATOR_AI_SUPERADMIN_PASSWORD"],
        )
