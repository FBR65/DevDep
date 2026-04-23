from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from models import User

def test_user_columns():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            username="alice",
            email="a@example.com",
            full_name="Alice",
            hashed_password="x",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "a@example.com"
        assert user.full_name == "Alice"
        assert user.bio is None
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)