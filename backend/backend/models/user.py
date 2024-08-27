from pydantic import BaseModel
from bson import ObjectId

class User(BaseModel):
    address: str = None
    api_token: str
    disabled: bool = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }
    
    def model_dump(self, *args, **kwargs):
        kwargs.setdefault('exclude', {'id'})
        return super().model_dump(*args, **kwargs)

