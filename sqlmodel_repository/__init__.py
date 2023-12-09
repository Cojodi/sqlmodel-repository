from typing import Any, Generic, Type, TypeVar

from pydantic import validate_model
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, select


def _update(self, obj: SQLModel | Any, **kwargs):
    if obj is not None:
        for k, v in obj.model_dump().items():
            setattr(self, k, v)

    for k, v in kwargs.items():
        setattr(self, k, v)

    *_, validation_error = validate_model(self.__class__, self.__dict__)
    if validation_error:
        raise validation_error

    return self


setattr(SQLModel, "update", _update)


T = TypeVar("T", bound=SQLModel)


class Repository(Generic[T]):
    def __init__(self, db, table_cls: Type[T]):
        self.db = db
        self.table_cls = table_cls

    def create(
        self,
        *,
        orm: SQLModel | None = None,
        **kwargs: T,
    ):
        if orm is not None:
            kwargs.update(orm.model_dump())

        o = self.table_cls(**kwargs)
        self.db.add(o)

        return o

    def update(self, o, *, orm: SQLModel | None = None, **kwargs):
        return o.update(orm, **kwargs)

    def first(
        self,
        *,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):  # pragma: no cover
        q = self._build_query(where, relationships, order_by)
        return self.db.exec(q).first()

    def one(
        self,
        *,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):  # pragma: no cover
        q = self._build_query(where, relationships, order_by)
        return self.db.exec(q).one()

    def all(
        self,
        *,
        where,
        relationships,
        order_by,
    ):  # pragma: no cover
        q = self._build_query(where, relationships, order_by)
        return self.db.exec(q).all()

    def _build_query(self, where, relationships, order_by):
        q = select(self.table_cls)
        if relationships is not None:
            for relationship in relationships:
                q = q.options(selectinload(relationship))

        if where is not None:
            q = q.where(where)

        if order_by is not None:
            for order_by_ in order_by:
                q = q.order_by(order_by_)

        return q


class AsyncRepository(Repository[T]):
    def __init__(self, db, table_cls):
        super().__init__(db, table_cls)

    async def first(
        self,
        *,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):
        q = self._build_query(where, relationships, order_by)
        return (await self.db.exec(q)).first()

    async def one(
        self,
        *,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):
        q = self._build_query(where, relationships, order_by)
        return (await self.db.exec(q)).one()

    async def all(
        self,
        *,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):
        q = self._build_query(where, relationships, order_by)
        return (await self.db.exec(q)).all()

    async def first_or_create(
        self,
        *,
        orm: SQLModel | None = None,
        where: bool | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
        **kwargs: T,
    ):
        o = await self.first(
            where=where, relationships=relationships, order_by=order_by
        )
        if o is None:
            o = self.create(orm=orm, **kwargs)
            await self.db.commit()
            await self.db.refresh(o)

        return o
