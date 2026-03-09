from sqlalchemy import Column, Integer, String
from .base import Base
from uuid import uuid4

class UserInfo(Base):
    __tablename__='user_info'
    __table_args__={"schema":"user_data"}
    id=Column(String, primary_key=True, index=True,default=lambda:str(uuid4()))
    name=Column(String)
    email=Column(String,unique=True, nullable=False)
    password=Column(String)

