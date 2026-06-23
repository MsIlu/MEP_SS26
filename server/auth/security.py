# Author: Ilu
# Created as part of the authentication and profile management implementation.
# This module contains password hashing, JWT handling, and authentication dependencies.

from datetime import datetime, timedelta, timezone
from typing import Optional

import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from database.connection import get_db_session
from database.models import User


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing. Please set it in the environment.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Stunden

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False,
)

def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it in the database.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against a stored password hash.
    """
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(account_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
   Create a signed JWT access token for the given account id.
   """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(account_id),
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_session():
    """
    Provide a database session for FastAPI dependencies.
    """
    with get_db_session() as session:
        yield session


def _resolve_account_from_token(token: str, session: Session) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account_id = payload.get("sub")

        if account_id is None:
            raise credentials_exception

        account_id = int(account_id)

    except (JWTError, ValueError):
        raise credentials_exception

    account = session.exec(
        select(User).where(User.id == account_id)
    ).first()

    if account is None:
        raise credentials_exception

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    return account


def get_current_account(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
) -> User:
    """
    Validate the bearer token and return the currently authenticated account.

    Raises 401 if the token is missing or invalid.
    Raises 403 if the account is inactive.
    """
    return _resolve_account_from_token(token, session)


def get_optional_current_account(
        token: str | None = Depends(optional_oauth2_scheme),
        session: Session = Depends(get_session),
) -> User | None:
    if token is None:
        return None

    return _resolve_account_from_token(token, session)
