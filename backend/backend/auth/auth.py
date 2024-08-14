import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

async def authenticate(auth_token: str = Header(None)):
    if (auth_token is None) or (auth_token != AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return True