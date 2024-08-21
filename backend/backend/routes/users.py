import datetime
import secrets
import string
from fastapi import APIRouter, Body, HTTPException, status, Depends
from backend.auth.auth import authenticate
from backend.config.database import users_collection
from backend.schemas.proof_request_schema import list_serial, individual_serial
from pymongo.errors import PyMongoError
from pydantic import BaseModel

router = APIRouter()

class WalletRequest(BaseModel):
    wallet: str

@router.post("/api_token")
async def create_api_token(
    request: WalletRequest,
    _ = Depends(authenticate),
):
    try:
        api_token = generate_unique_api_token()

        existing_token = users_collection.find_one({"wallet": request.wallet})

        if existing_token:
            users_collection.update_one(
                {"wallet": request.wallet},
                {"$set": {
                    "token": api_token,
                    "updated_at": datetime.datetime.utcnow()
                }}
            )
        else:
            token_document = {
                "wallet": request.wallet,
                "token": api_token,
                "created_at": datetime.datetime.utcnow(),
            }
            
            users_collection.insert_one(token_document)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed request: {str(e)}"
        )
    
    return { "api_token": api_token }

def generate_api_token(length=32):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

def generate_unique_api_token(length=32):
    while True:
        token = generate_api_token(length)
        if not users_collection.find_one({"token": token}):
            return token