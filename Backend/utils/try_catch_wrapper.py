from fastapi import HTTPException
import traceback
import functools

def catch_errors(func):
    @functools.wraps(func)  
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper