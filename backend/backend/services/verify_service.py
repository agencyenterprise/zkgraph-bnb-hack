import base64
import os
import dill
from bson import ObjectId
from datetime import datetime
from backend.blockchain.defender import RelayerClient
from backend.blockchain.transaction import encode_transaction_data, wait_for_confirmations
from zkgraph.verifier.verifier import ZkVerifier
from backend.config.database import proof_requests_collection

async def verify_proof(consumer_id: str, proof_request_id: str, worker_wallet: str, circuit: str, proof: str):
  print('Verifying proof for request ' + proof_request_id)

  layered_circuit = dill.loads(base64.b64decode(circuit))
  proof_transcript = base64.b64decode(proof)

  verifier = ZkVerifier(layered_circuit)
  verification = verifier.run_verifier(proof_transcript=proof_transcript)
  
  if verification:
    print('Proof verified for request ' + proof_request_id)

    proof_requests_collection.update_one(
      {
        "_id": ObjectId(proof_request_id)
      },
      {
        "$set": {
            "worker_wallet": worker_wallet,
            "proof": proof,
            "status": "VERIFIED",
            "verified_at": datetime.utcnow()
        }
      }
    )

    await pay_for_proof_request(proof_request_id)
  else:
    print('Proof verification failed for request ' + proof_request_id)
    proof_requests_collection.update_one(
      {
        "_id": ObjectId(proof_request_id)
      },
      {
        "$set": {
            "status": "FAILED"
        }
      }
    )

async def pay_for_proof_request(proof_request_id: str):
  print('Paying for proof request ' + proof_request_id)

  proof_request = proof_requests_collection.find_one({
    "_id": ObjectId(proof_request_id)
  })

  relayer = RelayerClient(os.getenv("DEFENDER_API_KEY"), os.getenv("DEFENDER_API_SECRET"))
  tx = relayer.send_transaction({
      "to": os.getenv("ESCROW_ADDRESS"),
      "data": encode_transaction_data("pay(address,address,uint256)", ["address", "address", "uint256"], [proof_request["owner_wallet"], proof_request["worker_wallet"], 1000000000000000]),
      "gasLimit": 1000000,
  })

  receipt = wait_for_confirmations(tx["hash"])
  
  if receipt["status"] == 0:
      raise Exception(f"Transaction failed: {tx['hash']}")
  
  proof_requests_collection.update_one(
    {
      "_id": ObjectId(proof_request_id)
    },
    {
      "$set": {
          "paid_at": datetime.utcnow()
      }
    }
  )