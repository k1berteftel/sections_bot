from datetime import datetime

from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs


class PostgresBuild:
    def __init__(self, url: str):
        self.engine = create_async_engine(url)

    async def create_tables(self, base):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def drop_tables(self, base):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)

    def session(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(self.engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PrivateUsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(VARCHAR)
    name: Mapped[str] = mapped_column(VARCHAR)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    entry = mapped_column(DateTime, nullable=False)
    subscription = mapped_column(DateTime, nullable=True)
    extension: Mapped[int] = mapped_column(Integer, default=0)


async def get_invite_bot_users():
    url = ''
    database = PostgresBuild(url)
    sessions = database.session()
    async with sessions() as session:
        result = await session.scalars(select(PrivateUsersTable))
    return result.fetchall()

