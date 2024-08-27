import json
from services.verify_service import verify_proof

async def handle_proof_message(body, consumer_id):
    payload = json.loads(body)
    await verify_proof(consumer_id, payload.get("proof_request_id"), payload.get("worker_wallet"), payload.get("circuit"), payload.get("proof"))
