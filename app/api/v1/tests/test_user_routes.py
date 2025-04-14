import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def mock_user():
    return User(id=1, username="testuser", password="hashed")


def test_get_user_found(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user

    mocker.patch("app.api.v1.routes_user.get_db", return_value=lambda: db_mock)

    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_not_found(mocker):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    mocker.patch("app.api.v1.routes_user.get_db", return_value=lambda: db_mock)

    response = client.get("/user/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_by_username_found(mocker, mock_user):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = mock_user

    mocker.patch("app.api.v1.routes_user.get_db", return_value=lambda: db_mock)

    response = client.get("/user-by-username/testuser")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_by_username_not_found(mocker):
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    mocker.patch("app.api.v1.routes_user.get_db", return_value=lambda: db_mock)

    response = client.get("/user-by-username/unknownuser")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_register_user(mocker):
    payload = {"username": "newuser", "password": "securepassword"}

    db_mock = MagicMock()
    db_user = MagicMock()
    db_user.id = 1
    db_user.username = payload["username"]
    db_mock.add.return_value = None
    db_mock.commit.return_value = None
    db_mock.refresh.return_value = None
    db_mock.query().filter().first.return_value = None

    mocker.patch("app.api.v1.routes_user.get_db", return_value=lambda: db_mock)
    mocker.patch("app.api.v1.routes_user.pwd_context.hash", return_value="hashedpassword")
    db_mock.refresh.return_value = db_user

    response = client.post("/register", json=payload)
    assert response.status_code == 200
    assert response.json()["username"] == payload["username"]
