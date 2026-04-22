# Specification: User Management System (FastAPI & SQLite)

## 1. Overview and Goals

This document specifies the requirements for a complete User Management System designed to be built with FastAPI and SQLite.

**Goals:**
1.  Implement secure user registration and authentication.
2.  Provide functionality for user profile management.
3.  Ensure data integrity and security through proper JWT-based authentication.
4.  Design a clear, well-defined API using RESTful principles.

## 2. Data Models

The system will manage three core entities: User, Profile, and Token (for security).

### 2.1. User Model
Stores core user authentication and identification data.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | Primary Key | PRIMARY KEY, Auto-increment |
| `email` | VARCHAR(255) | User's unique email address | UNIQUE, NOT NULL |
| `hashed_password` | VARCHAR(255) | Hashed password (using bcrypt/argon2) | NOT NULL |
| `created_at` | DATETIME | Timestamp of user creation | NOT NULL |

### 2.2. Profile Model
Stores additional user-specific details.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `user_id` | INTEGER | Foreign Key to User.id | FOREIGN KEY, NOT NULL |
| `username` | VARCHAR(100) | User-chosen unique username | UNIQUE, NOT NULL |
| `first_name` | VARCHAR(100) | User's first name | NOT NULL |
| `last_name` | VARCHAR(100) | User's last name | NOT NULL |
| `bio` | TEXT | Optional user biography | NULLable |

### 2.3. Token Model (Authentication)
Represents the JWT structure for session management.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `access_token` | VARCHAR(255) | JWT access token | NOT NULL |
| `refresh_token` | VARCHAR(255) | JWT refresh token | NOT NULL |
| `expires_at` | DATETIME | Expiration time of the access token | NOT NULL |

## 3. API Endpoints

All endpoints require authentication, except for registration.

### 3.1. Authentication Endpoints
| Path | Method | Description | Authentication Required | Request Body | Response Schema |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/auth/register` | POST | Register a new user | None | `email`, `password`, `username`, `first_name`, `last_name` | `{"message": "User created successfully"}` |
| `/auth/login` | POST | Authenticate user and return JWT | None | `email`, `password` | `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}` |
| `/auth/token/refresh` | POST | Refresh access token using refresh token | Bearer Token | `refresh_token` | `{"access_token": "...", "refresh_token": "..."}` |

### 3.2. Profile Endpoints
These endpoints require a valid JWT for access.

| Path | Method | Description | Authentication Required | Request Body | Response Schema |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/profile` | GET | Retrieve the authenticated user's profile | Bearer Token | None | Profile Data (based on Profile Model) |
| `/profile/update` | PUT | Update the authenticated user's profile | Bearer Token | `username`, `first_name`, `last_name`, `bio` | `{"message": "Profile updated successfully"}` |

## 4. Authentication Flow (JWT Handling)

1.  **Registration**: User submits credentials to `/auth/register`. Upon success, a new `User` record is created in SQLite.
2.  **Login**: User submits credentials to `/auth/login`.
    *   System verifies credentials against the hashed password in the database.
    *   If valid, the system generates a short-lived **Access Token** and a long-lived **Refresh Token**.
    *   Tokens are stored securely (e.g., in a secure cookie or database, depending on deployment strategy).
3.  **Profile Access**: Client sends the **Access Token** in the `Authorization: Bearer <token>` header.
    *   The FastAPI dependency checks the token's validity and extracts the User ID.
    *   If valid, the request proceeds to fetch the corresponding data from the **Profile Model** associated with that User ID.
4.  **Token Refresh**: When the Access Token expires, the client sends the **Refresh Token** to `/auth/token/refresh`.
    *   The system verifies the Refresh Token's validity and checks if it has been revoked.
    *   If valid, a new Access Token (and optionally a new Refresh Token) is issued.

## 5. Database Schema (SQLite)

The following tables will be created in the SQLite database.

### Table: `users`
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY |
| `email` | TEXT | UNIQUE, NOT NULL |
| `hashed_password` | TEXT | NOT NULL |
| `created_at` | DATETIME | NOT NULL |

### Table: `profiles`
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| `user_id` | INTEGER | PRIMARY KEY, FOREIGN KEY references `users(id)` |
| `username` | TEXT | UNIQUE, NOT NULL |
| `first_name` | TEXT | NOT NULL |
| `last_name` | TEXT | NOT NULL |
| `bio` | TEXT | NULLable |

## 6. File Structure Mapping

The project structure will follow a standard FastAPI layout:
```
user_management_system/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application setup
│   ├── crud.py           # Database interaction logic
│   ├── models.py         # Pydantic schemas and SQLAlchemy models
│   ├── schemas.py        # JWT/request/response schemas
│   ├── security.py       # JWT handling and password hashing utilities
│   └── crud.py
├── database.py           # Database connection logic
├── main.py               # Application entry point
└── requirements.txt
```

This completes the structure and specification for the project.