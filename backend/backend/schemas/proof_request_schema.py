def individual_serial(proof_request) -> dict:
    return {
        # "id": proof_request["_id"],
        "name": proof_request["name"],
        "description": proof_request["description"],
        "ai_model_name": proof_request["ai_model_name"],
        "ai_model_inputs": proof_request["ai_model_inputs"],
    }

def list_serial(proof_requests) -> list:
    return [individual_serial(proof_request) for proof_request in proof_requests]