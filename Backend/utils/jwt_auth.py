from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Cookie
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data, expire_time: timedelta = None):
    to_encode = {"user": str(data)}
    expire = datetime.now(timezone.utc) + (expire_time or timedelta(hours=2))  # fix 1
    to_encode["exp"] = expire
    encoded = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def verify_access_token(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")  # fix 2

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")  # fix 3

    data = payload.get("user")
    if not data:
        raise HTTPException(status_code=422, detail="User data not found in token")

    return data