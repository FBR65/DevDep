import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from dependencies import get_current_user
from models import User
from auth import hash_password, create_access_token

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            username="alice",
            email="alice@example.com",
            full_name="Alice",
            hashed_password=hash_password("secret"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        yield session

@pytest.mark.asyncio
async def test_get_current_user_success(session):
    token = create_access_token(data={"sub": "alice"})
    user = await get_current_user(token=token, db=session)
    assert user.username == "alice"

@pytest.mark.asyncio
async def test_get_current_user_missing_token(session):
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="", db=session)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(session):
    token = create_access_token(data={"sub": "nobody"})
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=session)
    assert exc.value.status_code == 401