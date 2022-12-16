import pytest
from sqlalchemy import create_engine
from scraper import init_db_tables

from sqlalchemy.orm import Session


@pytest.fixture
def test_db():
    engine = create_engine(f"sqlite:///:memory:", echo=True)
    init_db_tables(engine)
    with Session(engine) as session:
        yield session
