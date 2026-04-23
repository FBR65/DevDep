from datetime import datetime, timezone
from pydantic import ValidationError
import pytest
from schemas import UserCreate, UserUpdate, UserPublic, Token

def test_user_create_valid():
    uc = UserCreate(username="alice", email="a@example.com", password="secret", full_name="Alice")
    assert uc.username == "alice"
    assert uc.email == "a@example.com"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="not-an-email", password="secret", full_name="Alice")

def test_user_update_partial():
    uu = UserUpdate(bio="Just Alice")
    assert uu.bio == "Just Alice"
    assert uu.full_name is None
    assert uu.email is None

def test_token():
    t = Token(access_token="abc123", token_type="bearer")
    assert t.access_token == "abc123"
    assert t.token_type == "bearer"

def test_user_public_from_attributes():
    class FakeUser:
        id = 1
        username = "alice"
        full_name = "Alice"
        bio = "Hello"
        email = "alice@example.com"
        created_at = datetime.now(timezone.utc)

    up = UserPublic.model_validate(FakeUser())
    assert up.id == 1
    assert up.bio == "Hello"