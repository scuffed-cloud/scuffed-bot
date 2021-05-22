from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func, Integer, Column, ForeignKey, UniqueConstraint, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, relationship, selectinload, sessionmaker


Base = declarative_base()


class Server(Base):
    __tablename__ = "servers"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(String, primary_key=True, nullable=False)
    create_date = Column(DateTime, server_default=func.now())


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("server_id", "name"),)
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(String, ForeignKey("servers.id"))
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)


class Role(Base):
    __tablename__ = "roles"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(String, ForeignKey("servers.id"))
    name = Column(String, nullable=False)
    color = Column(Integer, nullable=True)


async def load_database(session_string):
    eng = create_async_engine(session_string)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return sessionmaker(eng, expire_on_commit=False, class_=AsyncSession)
