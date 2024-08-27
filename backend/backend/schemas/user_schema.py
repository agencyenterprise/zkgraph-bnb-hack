def individual_serial(user) -> dict:
    return {
        "address": str(user["address"]),
        "api_token": str(user["api_token"]) if user.get("api_token") is not None else None,
    }

def list_serial(proof_requests) -> list:
    return [individual_serial(proof_request) for proof_request in proof_requests]