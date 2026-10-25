import base64
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

# Допуск на расхождение часов между Telegram и сервером.
CLOCK_SKEW_S = 60


class InvalidInitData(Exception):
    pass


class InvalidToken(Exception):
    pass


def validate_init_data(
    init_data: str, bot_token: str, max_age_s: int, now: float | None = None
) -> dict:
    """Проверяет подпись Telegram initData и возраст auth_date; возвращает данные user."""
    if not bot_token:
        raise InvalidInitData("bot token is not configured")
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InvalidInitData("hash is missing")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise InvalidInitData("signature mismatch")

    try:
        auth_date = int(pairs["auth_date"])
    except (KeyError, ValueError) as exc:
        raise InvalidInitData("auth_date is missing or malformed") from exc
    current = time.time() if now is None else now
    if auth_date > current + CLOCK_SKEW_S or current - auth_date > max_age_s:
        raise InvalidInitData("auth_date is out of range")

    try:
        user = json.loads(pairs["user"])
        int(user["id"])
    except (KeyError, ValueError, TypeError) as exc:
        raise InvalidInitData("user is missing or malformed") from exc
    return user


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(payload: str, secret: str) -> str:
    return _b64(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())


def create_access_token(user_id: int, secret: str, ttl_s: int, now: float | None = None) -> str:
    if not secret:
        raise InvalidToken("app secret is not configured")
    issued = time.time() if now is None else now
    payload = _b64(json.dumps({"sub": user_id, "exp": int(issued) + ttl_s}).encode())
    return f"{payload}.{_sign(payload, secret)}"


def verify_access_token(token: str, secret: str, now: float | None = None) -> int:
    if not secret:
        raise InvalidToken("app secret is not configured")
    payload, _, signature = token.partition(".")
    if not payload or not hmac.compare_digest(_sign(payload, secret), signature):
        raise InvalidToken("bad signature")
    try:
        data = json.loads(_unb64(payload))
        user_id, exp = int(data["sub"]), int(data["exp"])
    except (KeyError, ValueError, TypeError) as exc:
        raise InvalidToken("malformed payload") from exc
    if (time.time() if now is None else now) >= exp:
        raise InvalidToken("token expired")
    return user_id
