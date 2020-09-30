import os
from datetime import timedelta, datetime
from typing import Optional

from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .schemas import TokenData
from database import crud
from database.db import SessionLocal
from database.schemas import User, UserCreate, TaskCreate, Task


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(db: Session, login: str, password: str) -> Optional[User]:
    user = crud.get_user(db, login)

    if not user:
        return None
    if not _verify_password(password, user.password):
        return None

    return user


def perform_registration(db: Session, user: UserCreate) -> dict:
    validation = _validate_data(db, user.login)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["detail"],
            headers={"WWW-Authenticate": "Bearer"}
        )

    new_user = crud.create_user(db, user)

    return {"status_code": status.HTTP_200_OK}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")

        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)

    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, login=token_data.login)
    if user is None:
        raise credentials_exception

    return user


def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    return crud.create_task(db, task, user_id)


def _validate_data(db: Session, login: str) -> dict:
    if crud.get_user(db, login):
        return {"is_valid": False, "detail": "username already exists"}

    return {"is_valid": True}


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
