from typing import Annotated, List
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select, SQLModel

from database import engine, get_session
from models import User
from schemas import UserCreate, UserPublic, UserPrivate, UserUpdate, Token
from auth import hash_password, verify_password, create_access_token
from limiter import limiter
from dependencies import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="User Management System",
    description="FastAPI + SQLModel user management with JWT auth",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, payload: UserCreate, db: SessionDep):
    existing = db.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    existing_email = db.exec(select(User).where(User.email == payload.email)).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=UserPrivate)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.put("/users/me", response_model=UserPrivate)
async def update_me(payload: UserUpdate, current_user: Annotated[User, Depends(get_current_user)], db: SessionDep):
    if payload.email is not None and payload.email != current_user.email:
        existing_email = db.exec(select(User).where(User.email == payload.email)).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        current_user.email = payload.email
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.bio is not None:
        current_user.bio = payload.bio
    current_user.updated_at = datetime.now(timezone.utc)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/users/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, db: SessionDep):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get("/users", response_model=List[UserPublic])
async def list_users(
    db: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    users = db.exec(select(User).offset(offset).limit(limit)).all()
    return users
