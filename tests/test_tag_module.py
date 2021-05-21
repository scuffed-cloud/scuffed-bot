from scuffed_bot.modules.tags import Tags
from scuffed_bot.database import Server, Tag
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
async def test_get_tag():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    tag_cog = Tags(None, db, logging)
    async with db() as session:
        async with session.begin():
            session.add_all(
                [
                    Tag(name="test_tag1", content="1", server_id="myserver"),
                    Tag(name="test_tag2", content="2", server_id="myserver"),
                ]
            )

    tag1 = await tag_cog.get_tag("test_tag1", "myserver")
    tag2 = await tag_cog.get_tag("test_tag2", "myserver")
    assert tag1.name == "test_tag1"
    assert tag2.name == "test_tag2"
    tags = await tag_cog.get_tags("myserver")
    assert len(tags) == 2


@pytest.mark.asyncio
async def test_tag_creation():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    tag_cog = Tags(None, db, logging)
    res = await tag_cog.create_tag("test_tag1", "scuffed-test", "myserver")
    assert res
    res = await tag_cog.create_tag("test_tag1", "scuffed-test", "myserver")
    assert not res
    async with db() as session:
        res = await session.execute(select(Tag).where(Server.id == "myserver"))
    tags = res.scalars().all()
    assert len(tags) == 1
    assert tags[0].name == "test_tag1"
    assert tags[0].content == "scuffed-test"


@pytest.mark.asyncio
async def test_tag_removal():
    db = await database.load_database(session_string)
    await create_server(db, "myserver")
    tag_cog = Tags(None, db, logging)
    await tag_cog.create_tag("test_tag1", "scuffed-test1", "myserver")
    await tag_cog.create_tag("test_tag2", "scuffed-test2", "myserver")
    res = await tag_cog.remove_tag("test_tag1", "myserver")
    assert res
    res = await tag_cog.remove_tag("test_tag1", "myserver")
    assert not res
    tags = await tag_cog.get_tags("myserver")
    assert len(tags) == 1
    assert tags[0].name == "test_tag2"
