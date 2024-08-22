import datetime
import secrets
import string
from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from backend.auth.auth import authenticate
from backend.config.database import users_collection

router = APIRouter()

class CreateApiTokenRequest(BaseModel):
    address: str

@router.post("/api_token")
async def create_api_token(
    request: CreateApiTokenRequest,
    _ = Depends(authenticate),
):
    try:
        api_token = generate_unique_api_token()

        existing_token = users_collection.find_one({"address": request.address})

        if existing_token:
            users_collection.update_one(
                {"address": request.address},
                {"$set": {
                    "api_token": api_token,
                    "updated_at": datetime.datetime.utcnow()
                }}
            )
        else:
            token_document = {
                "address": request.address,
                "api_token": api_token,
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
        api_token = generate_api_token(length)
        if not users_collection.find_one({"api_token": api_token}):
            return api_token