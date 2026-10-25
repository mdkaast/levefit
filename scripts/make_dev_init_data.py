"""Печатает подписанный initData для тестового пользователя (только для локальной разработки).

Использование: python scripts/make_dev_init_data.py [telegram_id] [username]
Токен бота берётся из apps/api/.env (BOT_TOKEN).
"""
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode


def bot_token() -> str:
    for line in (Path(__file__).parent.parent / "apps/api/.env").read_text(encoding="utf-8").splitlines():
        if line.startswith("BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("BOT_TOKEN не найден в apps/api/.env")


def main() -> None:
    telegram_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1001
    username = sys.argv[2] if len(sys.argv) > 2 else "tester"
    fields = {
        "auth_date": str(int(time.time())),
        "query_id": "DEV",
        "user": json.dumps(
            {"id": telegram_id, "username": username, "language_code": "ru"}, ensure_ascii=False
        ),
    }
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token().encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    print(urlencode(fields))


if __name__ == "__main__":
    main()
