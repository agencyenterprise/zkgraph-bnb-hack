def individual_serial(proof_request) -> dict:
    return {
        "id": proof_request._id,
        "name": proof_request.name,
        "description": proof_request.description,
    }

def list_serial(proof_requests) -> list:
    return [individual_serial(proof_request) for proof_request in proof_requests]