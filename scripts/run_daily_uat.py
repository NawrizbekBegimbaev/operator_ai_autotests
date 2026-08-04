#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASHKENT = ZoneInfo("Asia/Tashkent")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Изолированный запуск ежедневного happy-path UAT."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        help="Явный каталог прогона; по умолчанию uat-results/<timestamp>.",
    )
    parser.add_argument(
        "--telegram",
        choices=("auto", "always", "never", "dry-run"),
        default="auto",
        help="auto отправляет только при полной конфигурации; dry-run печатает отчёт.",
    )
    parser.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        help="Дополнительный аргумент pytest; можно указать несколько раз.",
    )
    parser.add_argument(
        "--capture-pytest-output",
        action="store_true",
        help=(
            "Сохранить сырой вывод pytest только в локальный pytest.log, "
            "не печатая его в публичный CI-лог."
        ),
    )
    return parser.parse_args()


def _run_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    stamp = datetime.now(TASHKENT).strftime("%Y%m%d-%H%M%S")
    return (PROJECT_ROOT / "uat-results" / stamp).resolve()


def main() -> int:
    args = _args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    run_dir = _run_dir(args.results_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    junit_path = run_dir / "junit.xml"
    artifact_dir = run_dir / "artifacts"
    env = os.environ.copy()
    env["OPERATOR_AI_ARTIFACT_DIR"] = str(artifact_dir)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "autotests/tests/uat",
        "-m",
        "daily_uat",
        "--junitxml",
        str(junit_path),
        *args.pytest_arg,
    ]
    if args.capture_pytest_output:
        pytest_log = run_dir / "pytest.log"
        with pytest_log.open("w", encoding="utf-8") as output:
            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                env=env,
                check=False,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
            )
    else:
        completed = subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=False)

    from autotests.uat.excel import (
        build_workbook,
        excel_file_name,
        render_caption_uz,
    )
    from autotests.uat.report import build_report, render_human_report, write_report_files
    from autotests.uat.telegram import (
        TelegramConfig,
        TelegramDeliveryError,
        send_document,
    )

    report = build_report(junit_path, pytest_returncode=completed.returncode)
    text_path, json_path = write_report_files(report, run_dir)
    report_text = render_human_report(report)
    excel_path = build_workbook(report, run_dir / "report.xlsx")
    caption = render_caption_uz(report)
    print("\n" + report_text)
    print(f"\nРезультаты: {run_dir}")
    print(f"Текст: {text_path}")
    print(f"JSON: {json_path}")
    print(f"Excel: {excel_path}")

    delivery_failed = False
    try:
        if args.telegram == "dry-run":
            print("\n[Telegram dry-run — подпись к файлу]\n" + caption)
        elif args.telegram != "never":
            config = TelegramConfig.from_env(required=args.telegram == "always")
            if config is None:
                print("Telegram: пропущено — TELEGRAM_BOT_TOKEN/CHAT_ID не настроены.")
            else:
                send_document(
                    config,
                    excel_path,
                    caption=caption,
                    file_name=excel_file_name(report),
                )
                print(f"Telegram: Excel-отчёт доставлен ({excel_file_name(report)}).")
    except TelegramDeliveryError as error:
        delivery_failed = True
        print(f"Telegram: ошибка доставки: {error}", file=sys.stderr)

    if delivery_failed or not report.is_green:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
