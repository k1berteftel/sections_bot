import datetime

from sqlalchemy import select, insert, update, column, text, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.model import (SchemesTable, MessagesTable, UsersTable, DeeplinksTable, OneTimeLinksIdsTable, AdminsTable)


class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def check_user(self, user_id: int) -> bool:
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return True if result else False

    async def add_user(self, user_id: int, username: str, name: str):
        if await self.check_user(user_id):
            return
        async with self._sessions() as session:
            await session.execute(insert(UsersTable).values(
                user_id=user_id,
                username=username,
                name=name
            ))
            await session.commit()

    async def add_entry(self, link: str):
        async with self._sessions() as session:
            await session.execute(update(DeeplinksTable).where(DeeplinksTable.link == link).values(
                entry=DeeplinksTable.entry+1
            ))
            await session.commit()

    async def add_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(DeeplinksTable).values(
                link=link
            ))
            await session.commit()

    async def add_link(self, link: str):
        async with self._sessions() as session:
            await session.execute(insert(OneTimeLinksIdsTable).values(
                link=link
            ))
            await session.commit()

    async def add_admin(self, user_id: int, name: str):
        async with self._sessions() as session:
            await session.execute(insert(AdminsTable).values(
                user_id=user_id,
                name=name
            ))
            await session.commit()

    async def add_scheme(self, name: str, deeplink: str, messages: list[dict]):
        async with self._sessions() as session:
            result = await session.execute(insert(SchemesTable).values(
                name=name,
                deeplink=deeplink
            ).returning(SchemesTable.id))
            scheme_id = result.scalar()
            for message in messages:
                session.add(
                    MessagesTable(
                        scheme_id=scheme_id,
                        message_id=message.get('message_id'),
                        chat_id=message.get('chat_id'),
                        button=message.get('button')
                    )
                )
            await session.commit()

    async def get_schemes(self):
        async with self._sessions() as session:
            result = await session.scalars(select(SchemesTable))
        return result.fetchall()

    async def get_scheme(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(SchemesTable).where(SchemesTable.id == id))
        return result

    async def get_scheme_messages(self, id: int):
        async with self._sessions() as session:
            result = await session.scalars(select(MessagesTable).where(MessagesTable.scheme_id == id)
                                           .order_by(asc(MessagesTable.id)))
        return result.fetchall()

    async def get_users(self):
        async with self._sessions() as session:
            result = await session.scalars(select(UsersTable))
        return result.fetchall()

    async def get_user(self, user_id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.user_id == user_id))
        return result

    async def get_user_by_username(self, username: str):
        async with self._sessions() as session:
            result = await session.scalar(select(UsersTable).where(UsersTable.username == username))
        return result

    async def get_links(self):
        async with self._sessions() as session:
            result = await session.scalars(select(OneTimeLinksIdsTable))
        return result.fetchall()

    async def get_admins(self):
        async with self._sessions() as session:
            result = await session.scalars(select(AdminsTable))
        return result.fetchall()

    async def get_deeplinks(self):
        async with self._sessions() as session:
            result = await session.scalars(select(DeeplinksTable))
        return result.fetchall()

    async def update_message(self, id: int, **kwargs):
        async with self._sessions() as session:
            await session.execute(update(MessagesTable).where(MessagesTable.id == id).values(
                kwargs
            ))
            await session.commit()

    async def set_scheme_name(self, id: int, name: str):
        async with self._sessions() as session:
            await session.execute(update(SchemesTable).where(SchemesTable.id == id).values(
                name=name
            ))
            await session.commit()

    async def set_activity(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                activity=datetime.datetime.today()
            ))
            await session.commit()

    async def set_active(self, user_id: int, active: int):
        async with self._sessions() as session:
            await session.execute(update(UsersTable).where(UsersTable.user_id == user_id).values(
                active=active
            ))
            await session.commit()

    async def del_deeplink(self, link: str):
        async with self._sessions() as session:
            await session.execute(delete(DeeplinksTable).where(DeeplinksTable.link == link))
            await session.commit()

    async def del_link(self, link_id: str):
        async with self._sessions() as session:
            await session.execute(delete(OneTimeLinksIdsTable).where(OneTimeLinksIdsTable.link == link_id))
            await session.commit()

    async def del_admin(self, user_id: int):
        async with self._sessions() as session:
            await session.execute(delete(AdminsTable).where(AdminsTable.user_id == user_id))
            await session.commit()

    async def del_message(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(MessagesTable).where(MessagesTable.id == id))
            await session.commit()

    async def del_scheme(self, id: int):
        async with self._sessions() as session:
            await session.execute(delete(SchemesTable).where(SchemesTable.id == id))
            await session.commit()
