from fastapi import APIRouter, Body, Depends, Path, HTTPException, status
from backend.models.proof_request import ProofRequest
from backend.auth.auth import authenticate
from backend.config.database import proof_requests_collection
from backend.schemas.proof_request_schema import list_serial, individual_serial
from backend.blockchain.transaction import encode_transaction_data
from backend.blockchain.defender import RelayerClient
from pymongo.errors import PyMongoError

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
    try:
        proofRequest = ProofRequest(
            owner_wallet=owner_wallet,
            name=name,
            description=description,
            ai_model_name=ai_model_name,
            ai_model_inputs=ai_model_inputs
        )
        result = proof_requests_collection.insert_one(proofRequest.dict())
        proofRequest._id = str(result.inserted_id)

        # relayer = RelayerClient("5C9HRJy8xdF5721GWrM9fW3eLJpfMKem", "y3bKPJekgiRXVVsHLVaJcPJ8p7uxuMXFtHgxzJ5SfxNbD4E9tEsW33gbNDSAKc2e")
        # relayer.send_transaction({
        #     "to": "0xec221396fe073e5c57b7A7c2C061F65bD5AE223F",
        #     "data": encode_transaction_data("lock(address payer, uint256 amount)", ["address", "uint256"], [owner_wallet, 1000000000000000000]),
        #     "gasLimit": 1000000,
        # })
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relayer transaction failed: {str(e)}"
        )



    # Send proof request to the queue
    # proof_request_message = {
    #     "proof_request_id": proofRequest._id,
    #     "ai_model_name": ai_model_name,
    #     "ai_model_inputs": ai_model_inputs,
    # }

    # proof_request_message_body = json.dumps(proof_request_message)
 
    # pika_client = PikaClient(os.environ.get("RABBITMQ_URL"))
    # await pika_client.publish("requests_queue", proof_request_message_body)

    return individual_serial(proofRequest.dict())
