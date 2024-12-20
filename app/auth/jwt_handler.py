# jwt_ handler. py
import time
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime
from fastapi import HTTPException
SECRET_KEY: str = "SECRET_KEY"
def create_access_token(user: str) -> str:
    payload = {"user": user, "expires": time.time() + 3600}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_access_token(token: str) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None:
            raise HTTPException(status_code=400, detail="No access token supplied")
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(403, detail="Token expired!")
        return data
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token" )