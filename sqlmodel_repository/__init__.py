from typing import Any, Generic, TypeVar

from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)


class Repository(Generic[T]):
    def __init__(self, db, table_cls: type[T]):
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
        kwargs.update(orm.model_dump() if orm is not None else {})
        return o.model_validate(kwargs)

    def first(
        self,
        *,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):  # pragma: no cover
        q = self._build_query(where, join_where, relationships, order_by)
        return self.db.exec(q).first()

    def one(
        self,
        *,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):  # pragma: no cover
        q = self._build_query(where, join_where, relationships, order_by)
        return self.db.exec(q).one()

    def all(
        self,
        *,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
        offset: int = 0,
        limit: int = 0,
    ):  # pragma: no cover
        q = self._build_query(where, join_where, relationships, order_by, offset, limit)
        return self.db.exec(q).all()

    def _build_query(
        self,
        where,
        join_where=None,
        relationships=None,
        order_by=None,
        offset: int = 0,
        limit: int = 0,
    ):
        q = select(self.table_cls)
        if limit > 0:
            q = q.offset(offset).limit(limit)

        if relationships is not None:
            for relationship in relationships:
                q = q.options(selectinload(relationship))

        if where is not None:
            q = q.where(where)

        if join_where is not None:
            for join_where_ in join_where:
                join_table, join_condition = join_where_
                q = q.join(join_table)
                q = q.where(join_condition)

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
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):
        q = self._build_query(where, join_where, relationships, order_by)
        return (await self.db.exec(q)).first()

    async def one(
        self,
        *,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
    ):
        q = self._build_query(where, join_where, relationships, order_by)
        return (await self.db.exec(q)).one()

    async def all(
        self,
        *,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
        offset: int = 0,
        limit: int = 0,
    ):
        q = self._build_query(where, join_where, relationships, order_by, offset, limit)
        return (await self.db.exec(q)).all()

    async def first_or_create(
        self,
        *,
        orm: SQLModel | None = None,
        where: bool | None = None,
        join_where: list[tuple[SQLModel, bool]] | None = None,
        relationships: list[Any] | None = None,
        order_by: list[Any] | None = None,
        **kwargs: T,
    ):
        o = await self.first(
            where=where,
            join_where=join_where,
            relationships=relationships,
            order_by=order_by,
        )
        if o is None:
            o = self.create(orm=orm, **kwargs)
            await self.db.commit()
            await self.db.refresh(o)

        return o
