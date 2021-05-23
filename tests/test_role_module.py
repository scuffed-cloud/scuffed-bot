from scuffed_bot.modules.roles import Roles
from scuffed_bot.database import Server, Role
import scuffed_bot.database as database
import logging
from sqlalchemy.future import select
import pytest

session_string = "sqlite+aiosqlite:///:memory:"


async def create_server(db, name):
    async with db() as session:
        async with session.begin():
            session.add(Server(id=name))


@pytest.mark.asyncio
async def test_get_role():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    role_cog = Roles(None, db, logging)
    async with db() as session:
        async with session.begin():
            session.add_all(
                [
                    Role(name="test_role1", color=1, server_id="myserver", id=1),
                    Role(name="test_role2", color=1, server_id="myserver", id=2),
                ]
            )

    role1 = await role_cog.get_role("test_role1", "myserver")
    role2 = await role_cog.get_role("test_role2", "myserver")
    assert role1.name == "test_role1"
    assert role2.name == "test_role2"
    roles = await role_cog.get_roles("myserver")
    assert len(roles) == 2


@pytest.mark.asyncio
async def test_role_creation():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    role_cog = Roles(None, db, logging)
    res = await role_cog.create_role("test_role1", 3, "myserver", 1)
    assert res
    res = await role_cog.create_role("test_role1", 1, "myserver", 2)
    assert not res
    async with db() as session:
        res = await session.execute(select(Role).where(Role.server_id == "myserver"))
    roles = res.scalars().all()
    assert len(roles) == 1
    assert roles[0].name == "test_role1"
    assert roles[0].color == 3


@pytest.mark.asyncio
async def test_role_removal():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    role_cog = Roles(None, db, logging)
    await role_cog.create_role("test_role1", 1, "myserver", 1)
    await role_cog.create_role("test_role2", 2, "myserver", 2)
    res = await role_cog.remove_role("test_role1", "myserver")
    assert res
    res = await role_cog.remove_role("test_role1", "myserver")
    assert not res
    roles = await role_cog.get_roles("myserver")
    assert len(roles) == 1
    assert roles[0].name == "test_role2"
