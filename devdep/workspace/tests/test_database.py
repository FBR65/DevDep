from sqlmodel import create_engine
from database import engine, get_session

def test_engine_is_sqlite():
    assert engine.url.database == "users.db"

def test_get_session_yields_session():
    gen = get_session()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        # generator exhausted as expected
        assert True