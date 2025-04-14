import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
import pyotp

client = TestClient(app)


@pytest.fixture
def fake_user():
    return User(
        id=1,
        username="testuser",
        password="$2b$12$2ePq5NzOVNQd4H9kh/nbVOubRT.hRnRtF8MzXzJvbbTTZg38RMoXK",
        is_2fa_enabled=False
    )


@pytest.fixture
def fake_user_2fa():
    secret = pyotp.random_base32()
    return User(
        id=2,
        username="user2fa",
        password="$2b$12$2ePq5NzOVNQd4H9kh/nbVOubRT.hRnRtF8MzXzJvbbTTZg38RMoXK",
        is_2fa_enabled=True,
        secret_key=secret
    )


def override_get_db():
    class DummyDB:
        def __init__(self):
            self.users = []

        def query(self, model):
            class Query:
                def __init__(self, users):
                    self.users = users

                def filter(self, cond):
                    username = cond.right.value if hasattr(cond.right, "value") else cond.right
                    filtered = [u for u in self.users if u.username == username or u.id == username]
                    return filtered

                def first(self):
                    return self.users[0] if self.users else None

            return Query(self.users)

        def commit(self): pass

    return DummyDB()


app.dependency_overrides[Session] = override_get_db


def test_login_success(mocker, fake_user):
    mock_db = override_get_db()
    mock_db.users.append(fake_user)

    mocker.patch("app.db.session.DBSession.get_db", return_value=mock_db)

    response = client.post("/login", json={
        "username": "testuser",
        "password": "password",
        "otp_code": None
    })

    assert response.status_code == 200
    assert "access_token" in response.json() or response.json()["requires_2fa"] is True


def test_login_invalid_user(mocker):
    mocker.patch("app.db.session.DBSession.get_db", return_value=override_get_db())

    response = client.post("/login", json={
        "username": "invalid",
        "password": "password",
        "otp_code": None
    })

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_enable_2fa(mocker, fake_user):
    mock_db = override_get_db()
    mock_db.users.append(fake_user)
    mocker.patch("app.db.session.DBSession.get_db", return_value=mock_db)

    response = client.post(f"/enable-2fa/{fake_user.id}")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_qr_code_success(mocker, fake_user_2fa):
    mock_db = override_get_db()
    mock_db.users.append(fake_user_2fa)
    mocker.patch("app.db.session.DBSession.get_db", return_value=mock_db)

    response = client.get(f"/qr-code/{fake_user_2fa.id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_login_2fa_unsuccess(mocker, fake_user_2fa):
    mock_db = override_get_db()
    mock_db.users.append(fake_user_2fa)
    mocker.patch("app.db.session.DBSession.get_db", return_value=mock_db)
    mocker.patch("app.services.user_service.authenticate_user_with_2fa", return_value=fake_user_2fa)

    totp = pyotp.TOTP(fake_user_2fa.secret_key)
    otp_code = totp.now()

    response = client.post("/login/2fa", json={
        "username": "teste",
        "password": "teste",
        "otp_code": otp_code
    })

    assert response.status_code == 400

