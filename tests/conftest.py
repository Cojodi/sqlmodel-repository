import pytest
from repository import Repo
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


@pytest.fixture(scope="function")
async def db_engine():
    from repository import UserDB, UserRelationshipDB

    url = "sqlite+aiosqlite:///tests/db.db"
    engine = create_async_engine(url)
    async with engine.begin() as c:
        await c.run_sync(SQLModel.metadata.create_all)
        yield engine
        await c.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
async def repo(db_engine):
    make_session = sessionmaker(db_engine, class_=Repo)
    async with make_session() as session:
        yield session
