def individual_serial(proof_request) -> dict:
    return {
        "id": str(proof_request["_id"]) if proof_request.get("_id") is not None else None,
        "name": str(proof_request["name"]),
        "description": str(proof_request["description"]),
        "ai_model_name": str(proof_request["ai_model_name"]),
        "ai_model_inputs": str(proof_request["ai_model_inputs"]),
        "status": str(proof_request["status"]),
        "worker_wallet": str(proof_request["worker_wallet"]),
        "proof": str(proof_request["proof"]),
    }

def list_serial(proof_requests) -> list:
    return [individual_serial(proof_request) for proof_request in proof_requests]