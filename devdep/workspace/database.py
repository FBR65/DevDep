from sqlmodel import create_engine, Session

SQLITE_FILE = "users.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE}"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

def get_session():
    with Session(engine) as session:
        yield session