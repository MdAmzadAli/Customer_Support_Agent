from sqlalchemy import select
from Database.schema import Appointment
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils import response_schema,parse_valid_date


async def check_availability(session: AsyncSession, date_str: str):
    ok, result = parse_valid_date(date_str)
    if not ok:
        return {"success": False, "message": result}   

    parsed_date = result   

    stmt = select(Appointment).where(Appointment.date == parsed_date)  
    appointment = await session.scalar(stmt)

    if not appointment:
        return response_schema(True, "Slot is available")
    return response_schema(False, "Slot is already booked")  