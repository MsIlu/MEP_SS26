# Created as part of the authentication and profile management test setup.
# Provides an isolated FastAPI test app with an in-memory SQLite database.

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from auth.router import router as auth_router
from auth.security import get_session
from profiles.router import router as profiles_router
from symptoms.router import router as symptoms_router


@pytest.fixture()
def db_session():
    """
    Create a fresh in-memory database session for each test.

    StaticPool keeps the same in-memory SQLite database available across
    all connections used during a single test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    """
    Create a FastAPI test client with auth and profile routers.

    The production database dependency is overridden so tests never touch
    the real PostgreSQL database.
    """
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(profiles_router)
    app.include_router(symptoms_router)

    def get_test_session():
        yield db_session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
