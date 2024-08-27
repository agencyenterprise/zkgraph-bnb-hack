from backend.models.user import User
from backend.config.database import users_collection

def get_user_api_token(api_token: str):
    user_data = users_collection.find_one({"api_token": api_token})
    if not user_data:
        return None
    
    return User(**user_data)