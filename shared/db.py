import os
import hashlib
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from shared.models import Base

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/anon.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def session_hash(tg_chat_id: int) -> str:
    """Short deterministic hash of chat_id for anonymous display in admin."""
    salt = os.getenv("SESSION_SECRET", "default_salt")
    return hashlib.sha256(f"{salt}:{tg_chat_id}".encode()).hexdigest()[:16]
