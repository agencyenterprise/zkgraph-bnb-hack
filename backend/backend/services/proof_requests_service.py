import os
import json
from fastapi import HTTPException, status
from backend.models.proof_request import ProofRequest
from backend.config.database import proof_requests_collection
from backend.schemas.proof_request_schema import individual_serial
from backend.blockchain.transaction import encode_transaction_data
from backend.blockchain.defender import RelayerClient
from pymongo.errors import PyMongoError
from backend.services.queue_service import PikaClient


async def create_proof_request(
    owner_wallet: str,
    name: str,
    description: str,
    ai_model_name: str,
    ai_model_inputs: str,
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

        relayer = RelayerClient(os.getenv("DEFENDER_API_KEY"), os.getenv("DEFENDER_API_SECRET"))
        relayer.send_transaction({
            "to": os.getenv("ESCROW_ADDRESS"),
            "data": encode_transaction_data("lock(address,uint256)", ["address", "uint256"], [owner_wallet, 1000000000000000]),
            "gasLimit": 1000000,
        })
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

    proof_request_message = {
        "proof_request_id": proofRequest._id,
        "ai_model_name": ai_model_name,
        "ai_model_inputs": ai_model_inputs,
    }

    proof_request_message_body = json.dumps(proof_request_message)
 
    pika_client = PikaClient(os.environ.get("RABBITMQ_URL"))
    await pika_client.publish("requests_queue", proof_request_message_body)

    return individual_serial(proofRequest.dict())