from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base
from uuid import uuid4
from sqlalchemy.sql import func

class Chats(Base):
    __tablename__='chats'
    __table_args__={"schema":"user_data"}
    id=Column(Integer, primary_key=True, autoincrement=True)
    user_message=Column(String, nullable=False)
    bot_response=Column(String, nullable=False)
    created_at=Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user_id=Column(String, ForeignKey('user_data.user_info.id'), nullable=False)
    