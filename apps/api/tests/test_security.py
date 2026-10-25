import time

import pytest

from app.security import (
    InvalidInitData,
    InvalidToken,
    create_access_token,
    validate_init_data,
    verify_access_token,
)
from tests.conftest import BOT_TOKEN, make_init_data


def test_valid_init_data_returns_user():
    user = validate_init_data(make_init_data(), BOT_TOKEN, 3600)
    assert user["id"] == 1001


def test_wrong_bot_token_rejected():
    with pytest.raises(InvalidInitData):
        validate_init_data(make_init_data(bot_token="other:TOKEN"), BOT_TOKEN, 3600)


def test_tampered_payload_rejected():
    tampered = make_init_data().replace("1001", "1002")
    with pytest.raises(InvalidInitData):
        validate_init_data(tampered, BOT_TOKEN, 3600)


def test_missing_hash_rejected():
    with pytest.raises(InvalidInitData):
        validate_init_data("auth_date=1&user=%7B%7D", BOT_TOKEN, 3600)


def test_expired_auth_date_rejected():
    old = make_init_data(auth_date=int(time.time()) - 7200)
    with pytest.raises(InvalidInitData):
        validate_init_data(old, BOT_TOKEN, 3600)


def test_future_auth_date_rejected():
    future = make_init_data(auth_date=int(time.time()) + 3600)
    with pytest.raises(InvalidInitData):
        validate_init_data(future, BOT_TOKEN, 3600)


def test_empty_bot_token_rejects_everything():
    with pytest.raises(InvalidInitData):
        validate_init_data(make_init_data(bot_token=""), "", 3600)


def test_token_roundtrip():
    token = create_access_token(7, "s", 60, now=1000)
    assert verify_access_token(token, "s", now=1030) == 7


def test_token_expires():
    token = create_access_token(7, "s", 60, now=1000)
    with pytest.raises(InvalidToken):
        verify_access_token(token, "s", now=1060)


def test_token_wrong_secret_or_tampered():
    token = create_access_token(7, "s", 60, now=1000)
    with pytest.raises(InvalidToken):
        verify_access_token(token, "other", now=1010)
    payload, _, sig = token.partition(".")
    with pytest.raises(InvalidToken):
        verify_access_token(f"{payload}x.{sig}", "s", now=1010)
