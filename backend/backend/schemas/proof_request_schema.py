def individual_serial(proof_request) -> dict:
    return {
        "id": str(proof_request["_id"]),
        "name": str(proof_request["name"]),
        "description": str(proof_request["description"]),
    }

def list_serial(proof_requests) -> list:
    return [individual_serial(proof_request) for proof_request in proof_requests]