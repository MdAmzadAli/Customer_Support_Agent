from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv,find_dotenv
import os
import asyncio
from .schema.base import Base
from . import schema

load_dotenv(find_dotenv())
DB_url=os.getenv("DATABASE_URL")
engine=create_async_engine(DB_url)

sessionLocal=async_sessionmaker(
    bind=engine,
    expire_on_commit=False
                                )

async def init_db():
    print("Tables known to Base:", Base.metadata.tables.keys())
    async with engine.begin() as conn:
          await conn.execute(text("CREATE SCHEMA IF NOT EXISTS user_data"))
          await conn.execute(text("CREATE SCHEMA IF NOT EXISTS appointment"))
          await conn.run_sync(Base.metadata.create_all)
          print("Done")
        
if __name__=="__main__":
     asyncio.run(init_db())
