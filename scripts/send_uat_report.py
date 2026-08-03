#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from autotests.uat.telegram import TelegramConfig, send_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Отправить готовый UAT-отчёт в Telegram.")
    parser.add_argument("report", type=Path, help="Путь к report.txt.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    text = args.report.read_text(encoding="utf-8").strip()
    if args.dry_run:
        print(text)
        return 0
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    config = TelegramConfig.from_env(required=True)
    assert config is not None
    count = send_report(config, text)
    print(f"Telegram: доставлено сообщений: {count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
