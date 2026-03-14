from ..utils.jwt_auth import verify_access_token,create_access_token
from fastapi import APIRouter, Depends, Response
from ..utils.try_catch_wrapper import catch_errors
from Database.schema import Chats,UserInfo
from Database.db_init import sessionLocal
from sqlalchemy import select,asc
from pydantic import BaseModel
from typing import List,Any

router = APIRouter()

# class ChatItem(BaseModel):
#     id: int
#     message: str        
#     created_at: str

class ChatResponse(BaseModel):
    chats: List[Any]


@router.get("/data")
@catch_errors
async def get_data(user_id: str = Depends(verify_access_token)):
    smtm = select(Chats).where(Chats.user_id == user_id).order_by(asc(Chats.created_at))

    async with sessionLocal.begin() as session:
        result = await session.scalars(smtm)
        rows = result.fetchall()   

    chat_items = [
    {
        "user_message": row.user_message,
        "bot_response": row.bot_response,
        "created_at": row.created_at
    }
    for row in rows
]
    return ChatResponse(chats=chat_items)

@router.get("/create")
@catch_errors
async def create_user(response:Response):
   async with sessionLocal.begin() as session:
       user=UserInfo()
       session.add(user)
    
   token=create_access_token(user.id)
   response.set_cookie(
       key="access_token",
       value=str(token),
       max_age=60*60*2,
       secure=False,
       samesite="lax",
       httponly=True
   )
   return {"response":"new user created"}





