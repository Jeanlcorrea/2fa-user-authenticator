import pytest
from unittest.mock import MagicMock
from app.models.user import User
from app.services.user_service import (
    hash_password,
    verify_password,
    create_access_token,
    authenticate_user_with_2fa,
    authenticate_user
)
from fastapi import HTTPException


@pytest.fixture
def mock_user():
    return User(id=1, username="testuser", password="hashedpassword", is_2fa_enabled=True, secret_key="base32secret")


def test_hash_password():
    password = "securepassword"
    hashed = hash_password(password)
    assert hashed != password


def test_verify_password_correct(mock_user):
    password = "securepassword"
    hashed = hash_password(password)
    result = verify_password(password, hashed)
    assert result is True


def test_verify_password_incorrect(mock_user):
    password = "securepassword"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)
    result = verify_password(wrong_password, hashed)
    assert result is False


def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None


def test_authenticate_user_success(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user
    mocker.patch("app.services.user_service.get_db", return_value=lambda: db_mock)

    result = authenticate_user(db_mock, "testuser", "correctpassword")
    assert result is mock_user


def test_authenticate_user_invalid_credentials(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user
    mocker.patch("app.services.user_service.get_db", return_value=lambda: db_mock)

    result = authenticate_user(db_mock, "testuser", "wrongpassword")
    assert result is None


def test_authenticate_user_with_2fa_success(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user
    mocker.patch("app.services.user_service.get_db", return_value=lambda: db_mock)

    totp_mock = MagicMock()
    totp_mock.verify.return_value = True
    mocker.patch("pyotp.TOTP", return_value=totp_mock)

    result = authenticate_user_with_2fa(db_mock, "testuser", "correctpassword", "123456")
    assert result is mock_user


def test_authenticate_user_with_2fa_missing_otp(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user
    mocker.patch("app.services.user_service.get_db", return_value=lambda: db_mock)

    with pytest.raises(HTTPException):
        authenticate_user_with_2fa(db_mock, "testuser", "correctpassword")


def test_authenticate_user_with_2fa_invalid_otp(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user
    mocker.patch("app.services.user_service.get_db", return_value=lambda: db_mock)

    totp_mock = MagicMock()
    totp_mock.verify.return_value = False
    mocker.patch("pyotp.TOTP", return_value=totp_mock)

    with pytest.raises(HTTPException):
        authenticate_user_with_2fa(db_mock, "testuser", "correctpassword", "invalid_otp")
