from __future__ import annotations

import time
from threading import Lock


class LoginRateGuard:
    """
    Не даёт служебным входам автотестов исчерпать staging rate limit.

    На стенде разрешено пять попыток входа в минуту с одного адреса. Интервал
    13 секунд оставляет небольшой запас и делает пакет парольных тестов
    безопасным для общих учётных записей.
    """

    def __init__(self, minimum_interval_seconds: float = 13.0) -> None:
        self.minimum_interval_seconds = minimum_interval_seconds
        self._last_attempt_at = 0.0
        self._lock = Lock()

    def before_attempt(self) -> None:
        with self._lock:
            elapsed = time.monotonic() - self._last_attempt_at
            remaining = self.minimum_interval_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
            self._last_attempt_at = time.monotonic()
