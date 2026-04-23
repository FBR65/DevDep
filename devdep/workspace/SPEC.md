# SPEC.md — User Management System

## 1. Overview & Goals

Build a complete **User Management System** using **FastAPI**, **SQLModel**, and **SQLite**. The system provides user registration, JWT-based authentication, and profile management via a RESTful API, with proper security, error handling, rate limiting, and auto-generated OpenAPI documentation.

### Goals
- Provide a secure, stateless authentication mechanism (JWT).
- Allow users to register, log in, manage their own profiles, and view public user listings.
- Ensure all sensitive operations use password hashing and token-based authorization.
- Deliver clean, well-documented API endpoints with consistent request/response schemas.
- Support rate limiting on authentication endpoints to mitigate brute-force attacks.

---

## 2. Functional Requirements

### 2.1 User Registration
- **Endpoint:** `POST /register`
- **Input:** `email`, `username`, `password`, `full_name`
- **Behavior:**
  - Validate that `email` is a valid email format.
  - Validate that `username` is unique.
  - Validate that `email` is unique.
  - Hash the raw password using `bcrypt` via `passlib`.
  - Store the new user in SQLite.
  - Return the created user object **without** including the password hash.
- **HTTP Status:** `201 Created` on success; `409 Conflict` if username/email already exists; `422 Unprocessable Entity` on validation failure.

### 2.2 User Authentication (Login)
- **Endpoint:** `POST /login`
- **Input:** `username`, `password` (x-www-form-urlencoded or JSON)
- **Behavior:**
  - Look up user by username.
  - Verify password against stored bcrypt hash.
  - If valid, generate a JWT access token with an expiration time.
  - Return the access token and token type (`bearer`).
- **HTTP Status:** `200 OK` on success; `401 Unauthorized` if credentials are invalid.

### 2.3 Profile Management
- **Get My Profile**
  - **Endpoint:** `GET /users/me`
  - **Auth:** Required (JWT `Authorization: Bearer <token>`).
  - **Returns:** Full profile of the authenticated user (excluding password).
  - **HTTP Status:** `200 OK`; `401 Unauthorized` if token missing/invalid.

- **Update My Profile**
  - **Endpoint:** `PUT /users/me`
  - **Auth:** Required.
  - **Input:** `full_name`, `email`, `bio` (all optional; partial updates allowed).
  - **Behavior:** Update only provided fields. Re-validate email uniqueness if changed.
  - **Returns:** Updated user object (excluding password).
  - **HTTP Status:** `200 OK`; `409 Conflict` if new email already taken; `401 Unauthorized` if token invalid.

- **Get Public Profile**
  - **Endpoint:** `GET /users/{user_id}`
  - **Auth:** Not required.
  - **Returns:** Public profile fields: `id`, `username`, `full_name`, `bio`.
  - **HTTP Status:** `200 OK`; `404 Not Found` if user does not exist.

### 2.4 User List
- **Endpoint:** `GET /users`
- **Auth:** Not required.
- **Query Parameters:**
  - `skip` (int, default `0`) — number of records to skip.
  - `limit` (int, default `20`, max `100`) — number of records to return.
- **Returns:** Paginated list of public user profiles.
- **HTTP Status:** `200 OK`.

---

## 3. Non-Functional Requirements

- **Performance:** SQLite is acceptable for the expected load. Use indexed lookups on `username` and `email`.
- **Security:**
  - Passwords are hashed with `bcrypt` (via `passlib`).
  - JWT tokens are signed with a symmetric secret (`HS256`).
  - Token expiry is enforced (default: 60 minutes).
  - Authentication endpoints (`/register`, `/login`) are rate-limited using `slowapi`.
- **Scalability:** Stateless JWT authentication means the API can scale horizontally if needed (secret must be shared across instances).
- **Maintainability:** Use modular file structure; separate concerns (models, schemas, auth, dependencies, routers).
- **Documentation:** Auto-generated OpenAPI/Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Testing:** Unit tests for hashing, token generation/validation, endpoint behavior. Integration tests for full request/response flows.

---

## 4. Data Model (SQLModel Schema)

### 4.1 `User` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `Integer` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique user identifier |
| `username` | `str` | `UNIQUE`, `NOT NULL`, `INDEX` | Public unique handle |
| `email` | `str` | `UNIQUE`, `NOT NULL`, `INDEX` | User email address |
| `full_name` | `str` | `NOT NULL` | Display name |
| `bio` | `str` | nullable, default `NULL` | Short biography |
| `hashed_password` | `str` | `NOT NULL` | Bcrypt-hashed password |
| `is_active` | `bool` | default `True` | Soft-delete / disable flag |
| `created_at` | `datetime` | default `func.now()` | Account creation timestamp |
| `updated_at` | `datetime` | default `func.now()` | Last update timestamp |

### 4.2 SQLModel Definition Reference

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

---

## 5. API Endpoints with Request/Response Schemas

### 5.1 Authentication Endpoints

#### `POST /register`
**Request Body:**
```json
{
  "email": "john@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "bio": null,
  "is_active": true,
  "created_at": "2025-01-01T12:00:00",
  "updated_at": "2025-01-01T12:00:00"
}
```

#### `POST /login`
**Request Body (JSON or form data):**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 5.2 User/Profile Endpoints

#### `GET /users/me`
**Headers:** `Authorization: Bearer <token>`

**Response (`200 OK`):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "bio": "FastAPI enthusiast",
  "is_active": true,
  "created_at": "2025-01-01T12:00:00",
  "updated_at": "2025-01-01T12:30:00"
}
```

#### `PUT /users/me`
**Headers:** `Authorization: Bearer <token>`

**Request Body (all fields optional):**
```json
{
  "full_name": "Johnny Doe",
  "email": "johnny@example.com",
  "bio": "Python developer and open-source contributor"
}
```

**Response (`200 OK`):** Same schema as `GET /users/me` with updated fields.

#### `GET /users/{user_id}`
**Response (`200 OK`):**
```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "John Doe",
  "bio": "FastAPI enthusiast"
}
```

#### `GET /users`
**Query:** `?skip=0&limit=20`

**Response (`200 OK`):**
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "full_name": "John Doe",
    "bio": "FastAPI enthusiast"
  }
]
```

### 5.3 Pydantic Schema Summary

| Schema | Purpose | Fields |
|--------|---------|--------|
| `UserBase` | Shared fields | `username`, `email`, `full_name`, `bio` |
| `UserCreate` | Registration request | `UserBase` + `password` |
| `UserPublic` | Public response | `id`, `username`, `full_name`, `bio` |
| `UserPrivate` | Authenticated response | `UserPublic` + `email`, `is_active`, `created_at`, `updated_at` |
| `UserUpdate` | Profile update | `full_name?: str`, `email?: str`, `bio?: str` |
| `Token` | Login response | `access_token: str`, `token_type: str` |

---

## 6. Authentication & Security Model

### 6.1 Password Hashing
- **Library:** `passlib[bcrypt]`
- **Algorithm:** `bcrypt`
- **Flow:**
  1. On registration: `pwd_context.hash(plain_password)` → store in `hashed_password`.
  2. On login: `pwd_context.verify(plain_password, hashed_password)`.

### 6.2 JWT Token Strategy
- **Library:** `python-jose[cryptography]`
- **Algorithm:** `HS256`
- **Token Payload:**
  ```json
  {
    "sub": "<username>",
    "exp": 1234567890,
    "iat": 1234567800
  }
  ```
- **Expiry:** Access tokens expire after 60 minutes.
- **Secret Key:** Loaded from environment variable `SECRET_KEY` (fallback to a dev-only default with a warning).

### 6.3 Dependency Injection
- `get_db()` — yields a SQLModel `Session`, committed/closed per request.
- `get_current_user(token, db)` — decodes JWT, fetches user from DB, raises `401` if invalid/missing.

### 6.4 Rate Limiting
- **Library:** `slowapi` (rate limiter based on `limits`)
- **Rules:**
  - `POST /register`: 5 requests per minute per IP.
  - `POST /login`: 5 requests per minute per IP.
- Returns `429 Too Many Requests` when exceeded.

### 6.5 CORS & Headers
- Not required for this standalone backend spec, but should be easy to add in `main.py` if a frontend is introduced later.

---

## 7. Error Handling Strategy

### 7.1 Global Error Format
All API errors return a consistent JSON structure:
```json
{
  "detail": "Error message here"
}
```

### 7.2 HTTP Status Codes by Scenario

| Scenario | Status | Detail Example |
|----------|--------|----------------|
| Validation failure (invalid email, short password) | `422` | Pydantic auto-generated |
| Duplicate username/email on register | `409` | `"Username already registered"` |
| Invalid login credentials | `401` | `"Incorrect username or password"` |
| Missing/invalid/expired token | `401` | `"Could not validate credentials"` |
| User not found (public profile) | `404` | `"User not found"` |
| Rate limit exceeded | `429` | `"Rate limit exceeded: 5 per 1 minute"` |

### 7.3 Implementation Pattern
- Use FastAPI `HTTPException` with appropriate status codes.
- Raise validation and business-logic errors inside route handlers.
- Keep error messages generic for auth failures (prevent user enumeration where reasonable).

---

## 8. Database Schema (SQLite)

### 8.1 Initialization
- Alembic is **not** used.
- On app startup, call `SQLModel.metadata.create_all(engine)` to create tables.
- Use `check_same_thread=False` with SQLite to allow FastAPI's async/sync thread interaction safely.

### 8.2 Engine & Session Setup
```python
from sqlmodel import create_engine, Session

sqlite_file = "users.db"
engine = create_engine(f"sqlite:///{sqlite_file}", connect_args={"check_same_thread": False})

# Run once on startup
SQLModel.metadata.create_all(engine)
```

---

## 9. File Structure Mapping

```
devdep/workspace/
├── main.py              # FastAPI app, routers, startup events
├── models.py            # SQLModel table definitions
├── schemas.py           # Pydantic request/response models
├── auth.py              # Password hashing & JWT encode/decode utils
├── dependencies.py      # get_db, get_current_user
├── database.py          # SQLModel engine & session setup
├── limiter.py           # slowapi Limiter instance & config
├── tests/
│   ├── __init__.py
│   ├── test_auth.py     # Register & login tests
│   ├── test_users.py    # Profile & listing tests
│   └── conftest.py      # pytest fixtures (TestClient, db override)
├── requirements.txt     # Project dependencies
└── SPEC.md              # This file
```

---

## 10. Testing Strategy

### 10.1 Unit Tests
- **Password hashing:** Verify `hash()` produces a string; `verify()` returns `True` for correct password, `False` otherwise.
- **JWT encode/decode:** Verify token contains correct `sub`, can be decoded with secret, fails with wrong secret, fails when expired.

### 10.2 Integration Tests (`TestClient`)
- **Registration:**
  - `201` on valid payload.
  - `409` on duplicate username/email.
  - `422` on invalid email format.
- **Login:**
  - `200` with token on valid credentials.
  - `401` on invalid password.
  - `429` after exceeding rate limit.
- **Profile:**
  - `200` for `GET /users/me` with valid token.
  - `401` for `GET /users/me` without token.
  - `200` for `PUT /users/me` with partial update.
  - `404` for `GET /users/{id}` with non-existent ID.
- **Listing:**
  - `200` for `GET /users` without auth.
  - Pagination logic: `skip` and `limit` respected.

### 10.3 Test Fixtures (`conftest.py`)
- Create an in-memory SQLite database (`sqlite:///:memory:`) for each test run to ensure isolation.
- Override `get_db` dependency to use the test session.
- Provide `client` fixture returning a `TestClient` instance with overridden dependencies.

### 10.4 Tools
- `pytest` + `httpx` (via `TestClient`) + `pytest-asyncio` if async tests are needed.
- Coverage goal: ≥ 90%.

---

## 11. Assumptions Made

1. **Single-role system:** No multi-role (admin/user) RBAC is required at this stage. All authenticated users have the same privileges.
2. **No email confirmation:** Registered users are immediately active (`is_active=True`). No email verification flow is implemented.
3. **No refresh tokens:** Only short-lived access tokens are provided. Token refresh/rotation is out of scope.
4. **SQLite for single-node deployment:** SQLite meets the requirements; no PostgreSQL/MySQL migration path is specified.
5. **Frontend-agnostic:** Tokens are returned in JSON; the client is responsible for storing and sending the `Authorization: Bearer <token>` header.
6. **No password reset flow:** Forgot-password / reset-password endpoints are out of scope.
7. **Bio field is optional on registration:** The `bio` is `NULL` by default and can only be set via `PUT /users/me` after registration.
8. **Username and email uniqueness are enforced at the database level and checked during registration to provide clean error messages.**
9. **Default dev SECRET_KEY:** If `SECRET_KEY` is not provided via environment, a hardcoded dev fallback is used with a logged warning. **Production must set a strong, random secret.**
10. **Slowapi rate limits are per-IP:** No advanced per-user rate limiting is required.

---

## 12. OpenAPI Documentation

- FastAPI automatically generates OpenAPI schema at `/openapi.json`.
- Interactive Swagger UI is available at `/docs`.
- Alternative ReDoc documentation at `/redoc`.
- All Pydantic schemas populate the "Schemas" section automatically.
- Security scheme `Bearer` is registered for token-protected endpoints.