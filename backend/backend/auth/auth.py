import os
from backend.services.user_service import get_user_api_token
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

async def authenticate_w_api_token(api_token: str = Header(None)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    user = get_user_api_token(api_token)
    if user is None:
        raise credential_exception

    return user

