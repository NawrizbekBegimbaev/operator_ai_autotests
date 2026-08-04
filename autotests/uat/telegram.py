from __future__ import annotations

import json
import mimetypes
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TELEGRAM_MESSAGE_LIMIT = 4096
TELEGRAM_CAPTION_LIMIT = 1024
TELEGRAM_DOCUMENT_LIMIT_BYTES = 50 * 1024 * 1024


class TelegramDeliveryError(RuntimeError):
    """Telegram не принял UAT-отчёт."""


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str
    thread_id: str = ""

    @classmethod
    def from_env(cls, *, required: bool) -> "TelegramConfig | None":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        thread_id = os.getenv("TELEGRAM_THREAD_ID", "").strip()
        if not token and not chat_id and not required:
            return None
        missing = [
            name
            for name, value in (
                ("TELEGRAM_BOT_TOKEN", token),
                ("TELEGRAM_CHAT_ID", chat_id),
            )
            if not value
        ]
        if missing:
            raise TelegramDeliveryError(
                "Не настроена Telegram-доставка: " + ", ".join(missing)
            )
        return cls(bot_token=token, chat_id=chat_id, thread_id=thread_id)


def split_message(text: str, *, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for line in text.splitlines():
        addition = len(line) + (1 if current else 0)
        if current and current_length + addition > limit:
            chunks.append("\n".join(current))
            current = []
            current_length = 0
        while len(line) > limit:
            if current:
                chunks.append("\n".join(current))
                current = []
                current_length = 0
            chunks.append(line[:limit])
            line = line[limit:]
        current.append(line)
        current_length += len(line) + (1 if current_length else 0)
    if current:
        chunks.append("\n".join(current))
    return chunks


def _perform(request: Request, *, timeout: int = 20) -> None:
    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        raise TelegramDeliveryError(
            f"Telegram вернул HTTP {error.code}; токен и chat ID не выводятся."
        ) from error
    except URLError as error:
        raise TelegramDeliveryError(
            f"Telegram недоступен: {error.reason}."
        ) from error
    try:
        body = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise TelegramDeliveryError("Telegram вернул не-JSON ответ.") from error
    if not isinstance(body, dict) or body.get("ok") is not True:
        description = body.get("description") if isinstance(body, dict) else None
        raise TelegramDeliveryError(
            f"Telegram отклонил сообщение: {description or 'неизвестная причина'}."
        )


def _send_chunk(config: TelegramConfig, text: str) -> None:
    payload = {"chat_id": config.chat_id, "text": text}
    if config.thread_id:
        payload["message_thread_id"] = config.thread_id
    _perform(
        Request(
            f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
            data=urlencode(payload).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
    )


def _multipart_body(
    fields: dict[str, str],
    *,
    file_field: str,
    file_name: str,
    file_bytes: bytes,
    boundary: str,
) -> bytes:
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )
    content_type = (
        mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_field}"; '
        f'filename="{file_name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
    )
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts)


def send_document(
    config: TelegramConfig,
    document: Path,
    *,
    caption: str = "",
    file_name: str | None = None,
) -> None:
    """Отправить Excel-отчёт файлом с короткой подписью."""
    if not document.exists():
        raise TelegramDeliveryError(f"Файл отчёта не найден: {document.name}.")
    payload_bytes = document.read_bytes()
    if len(payload_bytes) > TELEGRAM_DOCUMENT_LIMIT_BYTES:
        raise TelegramDeliveryError(
            f"Файл {document.name} превышает лимит Telegram в 50 МБ."
        )
    if len(caption) > TELEGRAM_CAPTION_LIMIT:
        caption = caption[: TELEGRAM_CAPTION_LIMIT - 1].rstrip() + "…"
    fields = {"chat_id": config.chat_id}
    if caption:
        fields["caption"] = caption
    if config.thread_id:
        fields["message_thread_id"] = config.thread_id
    boundary = f"----OperatorAIUAT{uuid.uuid4().hex}"
    body = _multipart_body(
        fields,
        file_field="document",
        file_name=file_name or document.name,
        file_bytes=payload_bytes,
        boundary=boundary,
    )
    _perform(
        Request(
            f"https://api.telegram.org/bot{config.bot_token}/sendDocument",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(body)),
            },
            method="POST",
        ),
        timeout=60,
    )


def send_report(config: TelegramConfig, text: str) -> int:
    chunks = split_message(text)
    for index, chunk in enumerate(chunks, start=1):
        prefix = f"({index}/{len(chunks)})\n" if len(chunks) > 1 else ""
        _send_chunk(config, prefix + chunk)
    return len(chunks)
