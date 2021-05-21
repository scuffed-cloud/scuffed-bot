import scuffed_bot.database as database
from sqlalchemy.future import select
import pytest

session_string = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_tag():
    db = await database.load_database(session_string)
    async with db() as session:
        async with session.begin():
            session.add(database.Server(id="myserver"))
        await session.commit()
        async with session.begin():
            session.add_all(
                [
                    database.Tag(server_id="myserver", name="tag1"),
                    database.Tag(server_id="myserver", name="tag2"),
                ]
            )
        await session.commit()

        results = await session.execute(
            select(database.Tag).where(database.Tag.server_id == "myserver")
        )
        tags = results.scalars().all()

    assert len(tags) == 2
    assert "tag1" in [x.name for x in tags]
