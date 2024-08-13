from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from models.id import ID

class ProofRequest(BaseModel):
    id: ID = None
    name: str
    description: str
    ai_model_name: str
    ai_model_inputs: str
    owner_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }

    def dict(self, *args, **kwargs):
        kwargs.setdefault('exclude', {'id'})
        return super().dict(*args, **kwargs)
    
    def model_dump(self, *args, **kwargs):
        kwargs.setdefault('exclude', {'id'})
        return super().model_dump(*args, **kwargs)
