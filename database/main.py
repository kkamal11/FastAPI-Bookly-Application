from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import env_config

from .models import Books, User, Reviews

engine = create_engine(
    url=env_config.DATABASE_URL,
    echo=env_config.ECHO_SQL,
    future=True
)

engine = AsyncEngine(engine)


async def init_db() -> None:
    async with engine.begin() as conn:
        # statement = text("""
        #                  SELECT 'HELLO'
        #                  """)
        # result = await conn.execute(statement)
        # print(result.all())
        from .books.models import Books
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session

