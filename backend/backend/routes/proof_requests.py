from fastapi import APIRouter, Body
from backend.models.proof_request import ProofRequest
from backend.config.database import proof_requests_collection
from backend.schemas.proof_request_schema import list_serial

router = APIRouter()

@router.get("/")
async def get_proof_requests():
    proofs = proof_requests_collection.find()
    return list_serial(proofs)

@router.post("/")
async def create_proof_request(
    name: str = Body(),
    description: str = Body(),
    ai_model_name: str = Body(),
    ai_model_inputs: str = Body(),
):
    proofRequest = ProofRequest(name=name, description=description, ai_model_name=ai_model_name, ai_model_inputs=ai_model_inputs)
    result = proof_requests_collection.insert_one(proofRequest.dict())
    inserted_id = str(result.inserted_id)
    
