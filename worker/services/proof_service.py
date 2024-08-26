import base64
import json
import os
import numpy as np
import onnx
import dill
from services.queue_service import PikaClient
from zkgraph.graph.engine import Value
from zkgraph.ops.from_onnx import from_onnx
from zkgraph.prover.prover import ZkProver

async def generate_proof(consumer_id: str, proof_request_id: str, ai_model_name: str, ai_model_inputs: str):
  print('Generating proof for request ' + proof_request_id + ' using worker: ' + consumer_id)

  onnx_model = onnx.load('models/' + ai_model_name + '.onnx')
  shape_info = onnx.shape_inference.infer_shapes(onnx_model)

  value_info_protos = []
  for node in shape_info.graph.value_info:
      value_info_protos.append(node)

  onnx_model.graph.output.extend(value_info_protos)

  onnx.checker.check_model(onnx_model)

  parsed_ai_model_inputs = json.loads(ai_model_inputs)
  inputs = np.array(parsed_ai_model_inputs)
  inputs = np.random.randn(1, 2).astype(np.float32)
  zerok_outputs = from_onnx(onnx_model, inputs)

  graph_output = np.sum(zerok_outputs[0])
  layered_circuit, _ = Value.compile_layered_circuit(graph_output)

  prover = ZkProver(layered_circuit)
  prover.prove()
  proof_transcript = prover.proof_transcript.to_bytes()
  # print(proof_transcript)

  pika_client = PikaClient(os.environ.get('RABBITMQ_URL'))

  await pika_client.publish("proofs_queue", json.dumps({
      'proof_request_id': proof_request_id,
      'worker_wallet': os.getenv("WORKER_WALLET"),
      'circuit': base64.b64encode(dill.dumps(layered_circuit)).decode(),
      'proof': base64.b64encode(proof_transcript).decode()
  }))
