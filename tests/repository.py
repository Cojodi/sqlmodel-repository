from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel_repository import AsyncRepository


class UserRelationshipDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="userdb.id")
    user: "UserDB" = Relationship(back_populates="relationships")

    value: str


class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    relationships: list[UserRelationshipDB] = Relationship(back_populates="user")


class UserRepository(AsyncRepository[UserDB]):
    def __init__(self, db):
        super().__init__(db, UserDB)


class UserRelationshipRepository(AsyncRepository[UserRelationshipDB]):
    def __init__(self, db):
        super().__init__(db, UserRelationshipDB)


class Repo(AsyncSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = UserRepository(self)
        self.relationship = UserRelationshipRepository(self)
