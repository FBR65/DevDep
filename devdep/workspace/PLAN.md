# Implementation Plan: User Management System

## Overview

Build a complete User Management System using FastAPI, SQLModel, and SQLite. The project provides RESTful endpoints for user registration, JWT-based authentication, profile management, and public user listing, protected by bcrypt password hashing, JWT token verification, and slowapi rate limiting. Every task follows Test-Driven Development (RED → GREEN → REFACTOR).

## File Structure Mapping

```
devdep/workspace/
├── requirements.txt          # Task 01
├── database.py               # Task 02
├── models.py                 # Task 03
├── schemas.py                # Task 04
├── auth.py                   # Task 05
├── limiter.py                # Task 06
├── dependencies.py             # Task 07
├── main.py                   # Task 08 + Task 09
├── tests/
│   ├── __init__.py           # Task 10
│   ├── conftest.py           # Task 10
│   ├── test_auth.py          # Task 11
│   └── test_users.py         # Task 11
└── PLAN.md                   # This file
```

## Task Dependency Graph

```
Task 01 (requirements.txt)
    │
    ├── Task 02 (database.py) ──┬── Task 03 (models.py)
    │                           │
    ├── Task 04 (schemas.py)    │
    │                           │
    ├── Task 05 (auth.py) ──────┼── Task 07 (dependencies.py)
    │                           │
    ├── Task 06 (limiter.py)    │
    │                           │
    └── Task 08 + 09 (main.py) ←┘
                                    │
                                Task 10 + 11 (tests)
```

---

## Tasks

### Task 01: Environment Setup — requirements.txt

**Goal:** Define and freeze all runtime and test dependencies with pinned versions.

**Input Artifacts:** SPEC.md §3, §6, §10

**Output Artifacts:** `requirements.txt`

**Dependencies:** None

**TDD Steps:**
- **RED:** Attempt to import `fastapi`, `sqlmodel`, `slowapi`, `passlib`, `python-jose`, `pytest`, and `httpx` in a fresh virtual environment — all imports fail.
- **GREEN:** Write `requirements.txt` with pinned versions for:
  - `fastapi==0.109.2`
  - `uvicorn[standard]==0.27.1`
  - `sqlmodel==0.0.16`
  - `slowapi==0.1.9`
  - `passlib[bcrypt]==1.7.4`
  - `python-jose[cryptography]==3.3.0`
  - `pydantic==2.6.1`
  - `pytest==8.0.0`
  - `httpx==0.26.0`
  - `pytest-asyncio==0.23.4`
  Install with `pip install -r requirements.txt`.
- **REFACTOR:** Verify each import succeeds; remove unused or redundant transitive pins.

**Acceptance Criteria:**
- [ ] `pip install -r requirements.txt` completes without errors.
- [ ] `python -c "import fastapi, sqlmodel, slowapi, passlib, jose, pytest, httpx"` succeeds.
- [ ] Every top-level dependency has a pinned version string.

---

### Task 02: Database Layer — database.py

**Goal:** Configure a SQLite engine and session factory using SQLModel, with `check_same_thread=False`.

**Input Artifacts:** `requirements.txt`, SPEC.md §8

**Output Artifacts:** `database.py`

**Dependencies:** Task 01

**TDD Steps:**
- **RED:** Write `tests/test_database.py` asserting that `from database import engine, SessionLocal` succeeds and `engine.url.database == "users.db"`. Run fails because `database.py` does not exist.
- **GREEN:** Implement `database.py`:
  ```python
  from sqlmodel import create_engine, Session

  SQLITE_FILE = "users.db"
  SQLITE_URL = f"sqlite:///{SQLITE_FILE}"

  engine = create_engine(
      SQLITE_URL,
      connect_args={"check_same_thread": False},
      echo=False,
  )

  def get_session() -> Session:
      with Session(engine) as session:
          yield session
  ```
  Re-run the test — it passes.
- **REFACTOR:** Confirm `engine` is a singleton; ensure `get_session` is a generator context manager (for dependency injection later).

**Acceptance Criteria:**
- [ ] `database.py` exports `engine` (a SQLModel `Engine`) and `get_session`.
- [ ] `engine` connects to `sqlite:///users.db` with `check_same_thread=False`.
- [ ] `get_session` yields a `Session` inside a `with` block and closes it.
- [ ] `pytest tests/test_database.py` passes.

---

### Task 03: SQLModel Models — models.py

**Goal:** Define the `User` SQLModel table with all fields, constraints, and indexes specified in the spec.

**Input Artifacts:** `database.py`, SPEC.md §4

**Output Artifacts:** `models.py`

**Dependencies:** Task 02

**TDD Steps:**
- **RED:** Write `tests/test_models.py` asserting:
  1. `User` can be instantiated with `username="alice", email="a@example.com", full_name="Alice", hashed_password="x"`.
  2. `User.__table__.columns` contains `id`, `username`, `email`, `full_name`, `bio`, `hashed_password`, `is_active`, `created_at`, `updated_at`.
  3. Calling `SQLModel.metadata.create_all(engine)` creates a `user` table with a primary key on `id`.
  Run fails because `models.py` is missing.
- **GREEN:** Implement `models.py`:
  ```python
  from typing import Optional
  from datetime import datetime
  from sqlmodel import SQLModel, Field, Relationship

  class User(SQLModel, table=True):
      __tablename__ = "user"

      id: Optional[int] = Field(default=None, primary_key=True)
      username: str = Field(index=True, nullable=False, unique=True)
      email: str = Field(index=True, nullable=False, unique=True)
      full_name: str = Field(nullable=False)
      bio: Optional[str] = Field(default=None, nullable=True)
      hashed_password: str = Field(nullable=False)
      is_active: bool = Field(default=True, nullable=False)
      created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)
      updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)
  ```
  Re-run the test — it passes.
- **REFACTOR:** Verify `Field()` constraints match the SPEC table exactly; ensure no extraneous imports.

**Acceptance Criteria:**
- [ ] `models.py` defines a single `User` class inheriting `SQLModel, table=True`.
- [ ] All columns from SPEC §4 are present with correct types, defaults, and nullability.
- [ ] `username` and `email` have `unique=True` and `index=True`.
- [ ] `SQLModel.metadata.create_all(engine)` succeeds and creates the `user` table.
- [ ] `pytest tests/test_models.py` passes.

---

### Task 04: Pydantic Schemas — schemas.py

**Goal:** Define all request/response Pydantic models used by the API.

**Input Artifacts:** SPEC.md §5.3

**Output Artifacts:** `schemas.py`

**Dependencies:** None (pure Pydantic)

**TDD Steps:**
- **RED:** Write `tests/test_schemas.py` asserting:
  1. `UserCreate` accepts `email`, `username`, `password`, `full_name` and validates email format.
  2. `UserCreate` rejects invalid email (`"not-an-email"`) with a `ValidationError`.
  3. `UserPublic` serializes to contain `id`, `username`, `full_name`, `bio`.
  4. `UserPrivate` additionally contains `email`, `is_active`, `created_at`, `updated_at`.
  5. `UserUpdate` allows partial updates: only `full_name` provided is valid.
  6. `Token` contains `access_token` and `token_type`.
  Run fails because `schemas.py` is missing.
- **GREEN:** Implement `schemas.py`:
  ```python
  from typing import Optional
  from datetime import datetime
  from pydantic import BaseModel, EmailStr, ConfigDict

  class UserBase(BaseModel):
      username: str
      email: EmailStr
      full_name: str
      bio: Optional[str] = None

  class UserCreate(UserBase):
      password: str

  class UserPublic(BaseModel):
      model_config = ConfigDict(from_attributes=True)
      id: int
      username: str
      full_name: str
      bio: Optional[str] = None

  class UserPrivate(UserPublic):
      email: EmailStr
      is_active: bool
      created_at: datetime
      updated_at: datetime

  class UserUpdate(BaseModel):
      full_name: Optional[str] = None
      email: Optional[EmailStr] = None
      bio: Optional[str] = None

  class Token(BaseModel):
      access_token: str
      token_type: str
  ```
  Re-run the test — all assertions pass.
- **REFACTOR:** Ensure no circular imports; verify `ConfigDict(from_attributes=True)` is used for ORM-mode serialization.

**Acceptance Criteria:**
- [ ] `schemas.py` exports: `UserBase`, `UserCreate`, `UserPublic`, `UserPrivate`, `UserUpdate`, `Token`.
- [ ] `UserCreate` validates email format via `EmailStr`.
- [ ] `UserUpdate` permits any subset of its fields.
- [ ] `UserPublic` and `UserPrivate` use `from_attributes=True` for SQLModel compatibility.
- [ ] `pytest tests/test_schemas.py` passes.

---

### Task 05: Security Layer — auth.py

**Goal:** Implement bcrypt password hashing and HS256 JWT creation/verification utilities.

**Input Artifacts:** `schemas.py` (for `Token` type usage in endpoint layer, but auth.py itself is self-contained), SPEC.md §6.1–§6.2

**Output Artifacts:** `auth.py`

**Dependencies:** Task 01 (libraries installed)

**TDD Steps:**
- **RED:** Write `tests/test_auth.py` (temporary unit tests) asserting:
  1. `hash_password("secret")` returns a non-empty string different from `"secret"`.
  2. `verify_password("secret", hash)` returns `True`; `verify_password("wrong", hash)` returns `False`.
  3. `create_access_token(data={"sub": "alice"})` returns a JWT string with two dots.
  4. `decode_access_token(valid_token)` returns payload with `"sub": "alice"` and `"exp"` present.
  5. `decode_access_token("bad.token.here")` raises a `JWTError`.
  6. `decode_access_token(token_created_with_wrong_secret)` raises a `JWTError`.
  Run fails because `auth.py` is missing.
- **GREEN:** Implement `auth.py`:
  ```python
  import os
  import warnings
  from datetime import datetime, timedelta, timezone
  from typing import Optional

  from jose import JWTError, jwt
  from passlib.context import CryptContext

  SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
  if SECRET_KEY == "dev-secret-key-change-in-production":
      warnings.warn("SECRET_KEY is using the insecure default. Set a strong SECRET_KEY env var.")

  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = 60

  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

  def hash_password(plain_password: str) -> str:
      return pwd_context.hash(plain_password)

  def verify_password(plain_password: str, hashed_password: str) -> bool:
      return pwd_context.verify(plain_password, hashed_password)

  def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
      to_encode = data.copy()
      if expires_delta:
          expire = datetime.now(timezone.utc) + expires_delta
      else:
          expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
      to_encode.update({"exp": expire})
      encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
      return encoded_jwt

  def decode_access_token(token: str) -> dict:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      return payload
  ```
  Re-run the test — they pass.
- **REFACTOR:** Extract constants to module-level variables; ensure `datetime.now(timezone.utc)` is used (not naive `datetime.utcnow` for expiry math consistency).

**Acceptance Criteria:**
- [ ] `auth.py` exports `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`.
- [ ] Password hashing uses `bcrypt` via `passlib`.
- [ ] JWT tokens use `HS256` and expire in 60 minutes by default.
- [ ] `SECRET_KEY` reads from env, falling back to a dev default with a logged warning.
- [ ] `decode_access_token` raises `JWTError` for invalid secret or malformed token.
- [ ] `pytest tests/test_auth.py` passes.

---

### Task 06: Rate Limiting — limiter.py

**Goal:** Configure a slowapi `Limiter` using in-memory storage and provide a reusable instance.

**Input Artifacts:** SPEC.md §6.4

**Output Artifacts:** `limiter.py`

**Dependencies:** Task 01

**TDD Steps:**
- **RED:** Write `tests/test_limiter.py` asserting that `from limiter import limiter` succeeds, `limiter` is a `slowapi.Limiter` instance, and `limiter._strategy` is not `None`. Run fails because `limiter.py` is missing.
- **GREEN:** Implement `limiter.py`:
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)
  ```
  Re-run the test — it passes.
- **REFACTOR:** Confirm `get_remote_address` is imported from `slowapi.util`; no additional configuration needed here (rate-limit decorators live in main.py).

**Acceptance Criteria:**
- [ ] `limiter.py` exports a `Limiter` instance named `limiter`.
- [ ] The limiter uses `get_remote_address` as its key function.
- [ ] `pytest tests/test_limiter.py` passes.

---

### Task 07: Dependencies — dependencies.py

**Goal:** Implement `get_db` (session dependency) and `get_current_user` (JWT validation dependency).

**Input Artifacts:** `database.py`, `models.py`, `auth.py`, SPEC.md §6.3

**Output Artifacts:** `dependencies.py`

**Dependencies:** Task 02, Task 03, Task 05

**TDD Steps:**
- **RED:** Write `tests/test_dependencies.py` asserting:
  1. Calling `get_db()` yields a session and closes it on generator exhaustion.
  2. `get_current_user` with a valid token for an existing user returns that `User` object.
  3. `get_current_user` with a missing token raises `401` with detail `"Could not validate credentials"`.
  4. `get_current_user` with a valid token for a non-existent user raises `401`.
  Run fails because `dependencies.py` is missing.
- **GREEN:** Implement `dependencies.py`:
  ```python
  from typing import Annotated
  from fastapi import Depends, HTTPException, status
  from fastapi.security import OAuth2PasswordBearer
  from sqlmodel import Session, select

  from database import get_session
  from models import User
  from auth import decode_access_token, JWTError

  oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

  SessionDep = Annotated[Session, Depends(get_session)]

  async def get_db() -> Session:
      with get_session() as session:
          yield session

  async def get_current_user(
      token: Annotated[str, Depends(oauth2_scheme)],
      db: SessionDep,
  ) -> User:
      credentials_exception = HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Could not validate credentials",
          headers={"WWW-Authenticate": "Bearer"},
      )
      try:
          payload = decode_access_token(token)
          username: str = payload.get("sub")
          if username is None:
              raise credentials_exception
      except JWTError:
          raise credentials_exception

      statement = select(User).where(User.username == username)
      user = db.exec(statement).first()
      if user is None:
          raise credentials_exception
      return user
  ```
  Re-run the test — passes.
- **REFACTOR:** Ensure `get_db` mirrors the spec’s dependency-injection pattern; confirm `get_current_user` uses `select()` from SQLModel.

**Acceptance Criteria:**
- [ ] `dependencies.py` exports `get_db`, `get_current_user`, `oauth2_scheme`.
- [ ] `get_db` yields a `Session` and closes it on context exit.
- [ ] `get_current_user` extracts `"sub"` from the JWT payload and queries the `User` table.
- [ ] Invalid or missing tokens raise `HTTPException(401, detail="Could not validate credentials")`.
- [ ] `pytest tests/test_dependencies.py` passes.

---

### Task 08: API Routes — main.py (Router Section)

**Goal:** Implement all RESTful endpoints: `POST /register`, `POST /login`, `GET /users/me`, `PUT /users/me`, `GET /users/{user_id}`, `GET /users`.

**Input Artifacts:** `models.py`, `schemas.py`, `auth.py`, `limiter.py`, `dependencies.py`, SPEC.md §2, §5, §7

**Output Artifacts:** `main.py` (partial — all endpoint handlers via `APIRouter`)

**Dependencies:** Task 03, Task 04, Task 05, Task 06, Task 07

**TDD Steps:**
- **RED:** Write integration tests in `tests/test_auth.py` and `tests/test_users.py` stubs that call each endpoint. All requests fail with 404 or 500 because routes do not exist.
- **GREEN:** Implement the router and all endpoints in `main.py`:
  1. Create `router = APIRouter()`.
  2. Implement `@router.post("/register", response_model=UserPrivate, status_code=201)`:
     - Validate uniqueness of `username` and `email` via DB query.
     - Hash password with `hash_password`.
     - Insert `User`, commit, refresh, return `UserPrivate`.
     - Raise `409` if duplicate.
  3. Implement `@router.post("/login", response_model=Token)` decorated with `@limiter.limit("5/minute")`:
     - Authenticate user by username.
     - `verify_password`; if invalid raise `401` with `"Incorrect username or password"`.
     - Create JWT with `create_access_token(data={"sub": user.username})`.
     - Return `Token`.
  4. Implement `@router.get("/users/me", response_model=UserPrivate)`:
     - Dependency: `get_current_user`.
     - Return authenticated user directly.
  5. Implement `@router.put("/users/me", response_model=UserPrivate)`:
     - Dependency: `get_current_user`.
     - Accept `UserUpdate` payload.
     - Re-validate email uniqueness if email is being changed.
     - Patch only provided fields onto the user model.
     - Commit and return refreshed user as `UserPrivate`.
  6. Implement `@router.get("/users/{user_id}", response_model=UserPublic)`:
     - No auth required.
     - Query user by ID; raise `404` if not found.
     - Return `UserPublic`.
  7. Implement `@router.get("/users", response_model=list[UserPublic])`:
     - No auth required.
     - Accept `skip: int = 0`, `limit: int = 20`.
     - Validate `limit <= 100` or raise `422`.
     - Query with `offset(skip).limit(limit)`, return list of `UserPublic`.
  Re-run the tests — they pass.
- **REFACTOR:** Extract common validation logic; ensure `response_model` excludes `hashed_password` automatically because it is not present in the output schemas.

**Acceptance Criteria:**
- [ ] All six endpoints from SPEC §2 are implemented and return correct HTTP status codes.
- [ ] `POST /register` returns `201` with `UserPrivate`; returns `409` on duplicate username/email; returns `422` on invalid data.
- [ ] `POST /login` returns `200` with `Token`; returns `401` for bad credentials; rate limited via `@limiter.limit("5/minute")`.
- [ ] `GET /users/me` and `PUT /users/me` require a valid Bearer token and return `401` without one.
- [ ] `PUT /users/me` supports partial updates and checks email uniqueness when email changes.
- [ ] `GET /users/{user_id}` returns `404` for missing users and `200` with `UserPublic` for existing users.
- [ ] `GET /users` respects `skip` and `limit` (max 100) and returns `list[UserPublic]`.
- [ ] All error responses follow the format `{"detail": "..."}` per SPEC §7.
- [ ] `pytest tests/test_auth.py` and `tests/test_users.py` pass.

---

### Task 09: Application Bootstrap — main.py (App Section)

**Goal:** Assemble the FastAPI application, register the router, attach the limiter, wire up the startup event to create SQLModel tables, and expose OpenAPI docs.

**Input Artifacts:** `main.py` (router section), `database.py`, `models.py`, `limiter.py`

**Output Artifacts:** `main.py` (complete file including both router and app bootstrap)

**Dependencies:** Task 08

**TDD Steps:**
- **RED:** Write `tests/test_bootstrap.py` asserting that:
  1. `from main import app` succeeds and `app` is a `FastAPI` instance.
  2. `app.routes` contains paths for `/register`, `/login`, `/users/me`, `/users/{user_id}`, `/users`.
  3. A startup event exists and calling `SQLModel.metadata.create_all(engine)` is triggered on first request.
  4. The OpenAPI schema at `/openapi.json` is reachable and contains the expected operation IDs or paths.
  Run fails because the app and startup event are not wired.
- **GREEN:** Add the bootstrap section to `main.py`:
  ```python
  from fastapi import FastAPI
  from slowapi import _rate_limit_exceeded_handler
  from slowapi.errors import RateLimitExceeded
  from sqlmodel import SQLModel
  from database import engine
  from limiter import limiter

  app = FastAPI(
      title="User Management System",
      description="FastAPI + SQLModel user management with JWT auth",
      version="1.0.0",
  )

  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

  @app.on_event("startup")
  def on_startup() -> None:
      SQLModel.metadata.create_all(engine)

  app.include_router(router)
  ```
  Re-run the tests — they pass.
- **REFACTOR:** Ensure `on_startup` is a sync function (SQLModel `create_all` is sync); confirm limiter exception handler is registered before startup.

**Acceptance Criteria:**
- [ ] `main.py` exports `app` (a `FastAPI` instance).
- [ ] Startup event creates all SQLModel tables via `SQLModel.metadata.create_all(engine)`.
- [ ] `app.state.limiter` is set to the limiter from `limiter.py`.
- [ ] `RateLimitExceeded` is handled by slowapi’s default handler.
- [ ] All router paths are reachable through the app (`TestClient(app).get("/users")` returns `200`).
- [ ] `/docs` and `/redoc` render OpenAPI documentation successfully.
- [ ] `pytest tests/test_bootstrap.py` passes.

---

### Task 10: Test Infrastructure

**Goal:** Create the `tests/` package, `conftest.py` with fixtures for an in-memory database, overridden dependencies, and a `TestClient`.

**Input Artifacts:** `main.py`, `database.py`, `dependencies.py`, `models.py`

**Output Artifacts:** `tests/__init__.py`, `tests/conftest.py`

**Dependencies:** Task 09

**TDD Steps:**
- **RED:** Run `pytest tests/`; it fails because `tests/` is not a package and `conftest.py` is missing.
- **GREEN:** Create the files:
  - `tests/__init__.py` (empty, marks directory as Python package).
  - `tests/conftest.py`:
    ```python
    import pytest
    from fastapi.testclient import TestClient
    from sqlmodel import Session, create_engine, SQLModel
    from sqlalchemy.pool import StaticPool

    from main import app
    from dependencies import get_db
    from models import User
    from auth import hash_password

    TEST_DATABASE_URL = "sqlite://"

    @pytest.fixture(name="session")
    def session_fixture():
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
        SQLModel.metadata.drop_all(engine)

    @pytest.fixture(name="client")
    def client_fixture(session: Session):
        def get_session_override():
            return session
        app.dependency_overrides[get_db] = get_session_override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture(name="create_user")
    def create_user_fixture(session: Session):
        def _create_user(username: str, email: str, password: str, full_name: str = "Test User"):
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        return _create_user
    ```
  Re-run `pytest tests/` — collection succeeds and fixture tests pass.
- **REFACTOR:** Confirm fixtures have `autouse=False` (explicit is better); ensure `StaticPool` is used for in-memory SQLite consistency across connections.

**Acceptance Criteria:**
- [ ] `tests/__init__.py` exists (can be empty).
- [ ] `tests/conftest.py` defines `session`, `client`, and `create_user` fixtures.
- [ ] The `session` fixture uses an in-memory SQLite database with `StaticPool`.
- [ ] The `client` fixture overrides `get_db` to inject the test session.
- [ ] The `create_user` fixture inserts a fully-formed `User` into the test DB.
- [ ] `pytest --collect-only tests/` lists fixtures without errors.

---

### Task 11: Test Suites — tests/test_auth.py & tests/test_users.py

**Goal:** Write comprehensive integration tests covering registration, login, rate limiting, profile management, public listing, pagination, and auth failure paths.

**Input Artifacts:** `main.py`, `schemas.py`, `auth.py`, `tests/conftest.py`, SPEC.md §10

**Output Artifacts:** `tests/test_auth.py`, `tests/test_users.py`

**Dependencies:** Task 09, Task 10

**TDD Steps:**
- **RED:** Write all test functions first without the underlying endpoint behavior verified (this is the final integration test layer). See tests fail on the RED run.
- **GREEN:** Ensure all previous tasks are complete so the tests turn GREEN.
- **REFACTOR:** Deduplicate test helpers; keep tests independent and stateless.

**tests/test_auth.py contents:**
1. `test_register_success` — POST `/register` → 201, response contains user without password.
2. `test_register_duplicate_username` — register once, POST again with same username → 409.
3. `test_register_duplicate_email` — register once, POST again with same email → 409.
4. `test_register_invalid_email` — POST with `"not-an-email"` → 422.
5. `test_login_success` — register user, POST `/login` → 200, token present.
6. `test_login_invalid_password` — register user, POST `/login` with wrong password → 401.
7. `test_login_nonexistent_user` — POST `/login` with unknown username → 401.
8. `test_rate_limit_login` — trigger `/login` more than 5 times in rapid succession → 429.

**tests/test_users.py contents:**
1. `test_get_me_success` — login, Bearer token, GET `/users/me` → 200 with full profile.
2. `test_get_me_unauthorized` — GET `/users/me` with no token → 401.
3. `test_get_me_invalid_token` — GET `/users/me` with bad token → 401.
4. `test_update_me_full` — PUT `/users/me` with `full_name`, `email`, `bio` → 200, fields updated.
5. `test_update_me_partial` — PUT `/users/me` with only `bio` → 200, other fields unchanged.
6. `test_update_me_duplicate_email` — create two users, second tries to update email to first’s email → 409.
7. `test_get_public_profile` — GET `/users/{id}` for existing user → 200 with `UserPublic` fields.
8. `test_get_public_profile_not_found` — GET `/users/99999` → 404.
9. `test_list_users` — create 3 users, GET `/users` → 200, list length 3.
10. `test_list_users_pagination` — create 5 users, GET `/users?skip=2&limit=2` → 200, exactly 2 items, IDs skip first 2.
11. `test_list_users_limit_max` — GET `/users?limit=200` → 422 (limit exceeds 100).
12. `test_list_users_no_auth` — GET `/users` without token → 200 (public endpoint).

**Acceptance Criteria:**
- [ ] `pytest tests/test_auth.py` passes with 100% of its tests green.
- [ ] `pytest tests/test_users.py` passes with 100% of its tests green.
- [ ] Combined `pytest tests/` run shows green across all modules.
- [ ] Coverage for `auth.py`, `dependencies.py`, `main.py` route handlers is ≥ 90%.
- [ ] No shared mutable state between tests.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SQLModel `table=True` model changes require table recreation | Medium | Medium | Use in-memory DB for tests; dev DB can be deleted on schema changes (no Alembic). |
| slowapi rate-limit decorator conflicts with FastAPI dependency injection | Low | Medium | Apply `@limiter.limit()` directly on path operation functions; verify with `TestClient` |
| JWT secret fallback in dev leaks to production | Low | High | Add an explicit warning on startup; require `SECRET_KEY` env var in CI/production |
| SQLite `check_same_thread=False` causes threading bugs in tests | Medium | Low | Use `StaticPool` in test fixture; use `connect_args` consistently |
| Pydantic v2 `EmailStr` behaves differently from v1 | Medium | Medium | Pin pydantic version; validate with an explicit test case for invalid email |

---

## Completion Checklist

- [ ] Task 01: requirements.txt exists and installs cleanly.
- [ ] Task 02: database.py exists with engine and session generator.
- [ ] Task 03: models.py defines the `User` SQLModel table exactly to spec.
- [ ] Task 04: schemas.py defines all six Pydantic schemas.
- [ ] Task 05: auth.py implements bcrypt hashing and HS256 JWT encode/decode.
- [ ] Task 06: limiter.py exports a slowapi `Limiter` instance.
- [ ] Task 07: dependencies.py implements `get_db` and `get_current_user`.
- [ ] Task 08: main.py contains all six endpoint implementations.
- [ ] Task 09: main.py contains FastAPI app, startup event, limiter registration, and router inclusion.
- [ ] Task 10: tests/__init__.py and tests/conftest.py provide isolated fixtures.
- [ ] Task 11: tests/test_auth.py and tests/test_users.py cover all functional requirements with green tests.