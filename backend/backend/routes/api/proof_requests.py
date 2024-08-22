from fastapi import APIRouter, Body, Depends, Path
from backend.auth.auth import authenticate_w_api_token
from backend.config.database import proof_requests_collection
from backend.schemas.proof_request_schema import list_serial
from backend.services.proof_requests_service import create_proof_request

router = APIRouter()

@router.get("/{owner_wallet}")
async def get_proof_requests(
    owner_wallet: str = Path(..., alias="owner_wallet"),
    _ = Depends(authenticate_w_api_token),
):
    proofs = proof_requests_collection.find({"owner_wallet": owner_wallet })
    return list_serial(proofs)

@router.post("/")
async def create_proof_request_endpoint(
    name: str = Body(),
    description: str = Body(),
    ai_model_name: str = Body(),
    ai_model_inputs: str = Body(),
    user = Depends(authenticate_w_api_token),
):
    return await create_proof_request(
        user.address,
        name,
        description,
        ai_model_name,
        ai_model_inputs,
    )
