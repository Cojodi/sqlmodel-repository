import pytest
from repository import Repo, UserDB
from sqlmodel import SQLModel


@pytest.mark.asyncio
async def test_create_kwargs(repo: Repo):
    user = repo.user.create(username="user1")
    await repo.commit()
    await repo.refresh(user)

    assert user.id == 1


@pytest.mark.asyncio
async def test_create_orm(repo: Repo):
    user = repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()
    await repo.refresh(user)

    assert user.id == 1


@pytest.mark.asyncio
async def test_find(repo: Repo):
    expect = repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()
    await repo.refresh(expect)

    actual = await repo.user.first(where=UserDB.username == "user1")
    assert actual.model_dump() == expect.model_dump()

    actual = await repo.user.one(where=UserDB.username == "user1")
    assert actual.model_dump() == expect.model_dump()

    actual = await repo.user.all(where=UserDB.username == "user1")
    assert len(actual) == 1
    assert actual[0].model_dump() == expect.model_dump()


@pytest.mark.asyncio
async def test_first_or_create(repo: Repo):
    actual = await repo.user.first_or_create(
        where=UserDB.username == "user1", username="user1"
    )
    assert actual.id == 1
    assert actual.username == "user1"

    actual = await repo.user.first_or_create(
        where=UserDB.username == "user1", username="user1"
    )
    assert actual.id == 1
    assert actual.username == "user1"


@pytest.mark.asyncio
async def test_update(repo: Repo):
    expect = repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()

    expect = repo.user.update(expect, username="user2")
    await repo.commit()
    assert expect.username == "user2"


@pytest.mark.asyncio
async def test_update_from_orm(repo: Repo):
    expect = repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()

    class UserIn(SQLModel):
        username: str

    expect = repo.user.update(expect, orm=UserIn(username="user2"))
    await repo.commit()
    assert expect.username == "user2"


@pytest.mark.asyncio
async def test_load_relationship(repo: Repo):
    user = repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()
    await repo.refresh(user)

    user_relationship = repo.relationship.create(user_id=user.id, value="value1")
    await repo.commit()
    await repo.refresh(user_relationship)

    user = await repo.user.first(
        where=UserDB.id == 1, relationships=[UserDB.relationships]
    )
    assert len(user.relationships) == 1
    assert user.relationships[0].model_dump() == user_relationship.model_dump()


@pytest.mark.asyncio
async def test_order_by(repo: Repo):
    repo.user.create(orm=UserDB(username="user2"))
    repo.user.create(orm=UserDB(username="user1"))
    await repo.commit()

    actual = await repo.user.all(order_by=[UserDB.id])
    assert actual[0].id == 1
    assert actual[1].id == 2

    actual = await repo.user.all(order_by=[UserDB.username])
    assert actual[0].id == 2
    assert actual[1].id == 1
