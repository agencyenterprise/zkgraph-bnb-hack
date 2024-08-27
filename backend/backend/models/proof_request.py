from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from backend.models.id import ID

class ProofRequestStatus(str, Enum):
    PROCESSED = "PROCESSED"
    PROCESSING = "PROCESSING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

class ProofRequest(BaseModel):
    id: ID = None
    name: str
    owner_wallet: str
    description: str
    ai_model_name: str
    ai_model_inputs: str
    status: ProofRequestStatus = ProofRequestStatus.PROCESSING
    worker_wallet: str = None
    proof: str = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: datetime = None
    paid_at: datetime = None

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
