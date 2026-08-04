#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from autotests.uat.excel import build_workbook, excel_file_name, render_caption_uz
from autotests.uat.report import load_report
from autotests.uat.telegram import TelegramConfig, send_document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Отправить готовый Excel-отчёт UAT в Telegram-группу."
    )
    parser.add_argument(
        "run",
        type=Path,
        help="Каталог прогона uat-results/<run> или любой файл внутри него.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать подпись к файлу и путь к Excel, ничего не отправляя.",
    )
    args = parser.parse_args()

    run_dir = args.run if args.run.is_dir() else args.run.parent
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        print(f"Не найден {summary_path}.", file=sys.stderr)
        return 1

    report = load_report(summary_path)
    excel_path = run_dir / "report.xlsx"
    if not excel_path.exists():
        build_workbook(report, excel_path)
    caption = render_caption_uz(report)

    if args.dry_run:
        print(caption)
        print(f"\nФайл: {excel_path} → {excel_file_name(report)}")
        return 0

    load_dotenv(PROJECT_ROOT / ".env", override=False)
    config = TelegramConfig.from_env(required=True)
    assert config is not None
    send_document(
        config,
        excel_path,
        caption=caption,
        file_name=excel_file_name(report),
    )
    print(f"Telegram: Excel-отчёт доставлен ({excel_file_name(report)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
