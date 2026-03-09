from sqlalchemy import select
from Database.schema import Appointment
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils import response_schema,parse_valid_date

async def delete_appointment(session:AsyncSession, name:str, date:str):

    if not name.strip():
        return response_schema(False,"User name can't be empty")
    
    ok,result_date=parse_valid_date(date)
    
    if not ok:
        return response_schema(False, result_date)

    smtm=select(Appointment).where(
        Appointment.name==name,
        Appointment.date==result_date
    )
    result=await session.scalar(smtm)

    if not result:
        return response_schema(False, "No appointment found")
    
    await session.delete(result)
    return response_schema(True, "Appointment deleted successfully")
    
    
