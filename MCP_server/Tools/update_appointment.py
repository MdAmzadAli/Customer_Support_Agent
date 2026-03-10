from sqlalchemy import select
from Database.schema import Appointment
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils import response_schema,parse_valid_date


async def update_appointment(session:AsyncSession, name:str, date:str, newName:str="", newDate:str="",newReason:str=""):
    
    if not name.strip():
        return response_schema(False,"User name can't be empty")
    
    ok,result_date=parse_valid_date(date)

    if not ok:
       return response_schema(False, result_date)

    smtm=select(Appointment).where(
        Appointment.name==name,
        Appointment.date==result_date
    )
    apt=await session.scalar(smtm)
    
    if not apt:
        return response_schema(False, "Appointment Not Found")

    if newName.strip():
        apt.name=newName

    if newDate.strip():
        ok,newDate_result=parse_valid_date(newDate)
        if not ok:
            return response_schema(False,newDate_result)
        apt.date=newDate_result

    if newReason.strip():
        apt.reason=newReason
    
    await session.flush()
    return response_schema(True, "Appointment Updated successfully",{
        "appointment_id": str(apt.id),
        "name":           apt.name,
        "date":           apt.date.isoformat(),   
        "reason":         apt.reason,
    })
    
    
