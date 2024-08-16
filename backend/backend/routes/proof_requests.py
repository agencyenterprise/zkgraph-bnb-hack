from fastapi import APIRouter, Body, Depends, Path
from backend.models.proof_request import ProofRequest
from backend.auth.auth import authenticate
from backend.config.database import proof_requests_collection
from backend.schemas.proof_request_schema import list_serial, individual_serial

router = APIRouter()

@router.get("/{owner_wallet}")
async def get_proof_requests(
    owner_wallet: str = Path(..., alias="owner_wallet"),
    _ = Depends(authenticate),
):
    proofs = proof_requests_collection.find({"owner_wallet": owner_wallet })
    return list_serial(proofs)

@router.post("/")
async def create_proof_request(
    owner_wallet: str = Body(),
    name: str = Body(),
    description: str = Body(),
    ai_model_name: str = Body(),
    ai_model_inputs: str = Body(),
    _ = Depends(authenticate),
):
    proofRequest = ProofRequest(
        owner_wallet=owner_wallet,
        name=name,
        description=description,
        ai_model_name=ai_model_name,
        ai_model_inputs=ai_model_inputs
    )
    result = proof_requests_collection.insert_one(proofRequest.dict())
    proofRequest._id = str(result.inserted_id)
    return individual_serial(proofRequest.dict())
    
