from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest
from fastapi.testclient import TestClient

from main import app, get_session


@pytest.fixture(name="client")
def client_fixture():
    # A fresh, in-memory SQLite database for every single test — nothing
    # persists between tests, and we never touch the real books.db.
    # StaticPool + check_same_thread=False is needed because an in-memory
    # SQLite database normally disappears as soon as its connection closes;
    # this keeps the same connection alive for the lifetime of the test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    # This is the key trick: FastAPI lets you swap out any `Depends(...)`
    # for a different function, just for tests. Every endpoint that asks
    # for `Depends(get_session)` gets `get_session_override` instead,
    # without the endpoint code itself changing at all.
    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
