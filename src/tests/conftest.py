from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest

from database.main import get_session
from src.auth.dependencies import RoleChecker, AccessTokenBearer, RefreshTokenBearer

from main import app

mock_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()

def get_mock_session():
    yield mock_session

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(['admin'])


app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = role_checker
app.dependency_overrides[refresh_token_bearer] = refresh_token_bearer

@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_user_service():
    return mock_user_service
@pytest.fixture
def fake_book_service():
    return mock_book_service

@pytest.fixture
def test_client():
    return TestClient(app)

