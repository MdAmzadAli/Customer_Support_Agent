from sqlalchemy import select
from Database.schema import Appointment
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils import response_schema, parse_valid_date
from .check_availability import check_availability


async def book_appointment(session: AsyncSession, name: str, date: str, reason: str):
    
    if not name.strip() or not reason.strip():
        return response_schema(False,"Username or reason can't be empty")
    
    ok, result_date = parse_valid_date(date)
    if not ok:
        return response_schema(False, result_date)   

 
    available = await check_availability(session, result_date)
    if not available["success"]:
        return response_schema(False, "Slot already booked")

    
    apt = Appointment(
        name=name,
        date=result_date,   
        reason=reason,
    )
    session.add(apt)
    await session.flush()

  
    return response_schema(True, "Appointment booked successfully", {
        "appointment_id": str(apt.id),
        "name":           apt.name,
        "date":           apt.date.isoformat(),   
        "reason":         apt.reason,
    })