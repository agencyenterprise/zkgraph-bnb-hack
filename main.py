from zkgraph.polynomials.field import dequantization
import time
import numpy as np
import onnx
import onnxruntime
import os
from zkgraph.graph.engine import Value
from zkgraph.ops.onnx_utils import generate_small_iris_onnx_model
from zkgraph.ops.from_onnx import from_onnx
from zkgraph.prover.prover import ZkProver
from zkgraph.verifier.verifier import ZkVerifier


def add_intermediate_layers_as_outputs(onnx_model):
    """takes an onnx model and returns the same model but will all intermediate
    node outputs as outputs to the model.

    Useful for testing that all nodes are calculated correctly
    """

    shape_info = onnx.shape_inference.infer_shapes(onnx_model)

    value_info_protos = []
    for node in shape_info.graph.value_info:
        value_info_protos.append(node)

    onnx_model.graph.output.extend(value_info_protos)

    onnx.checker.check_model(onnx_model)

    return onnx_model


def main():
    np.random.seed(42)
    if "iris_model.onnx" not in os.listdir("tests/assets/"):
        generate_small_iris_onnx_model(onnx_output_path="tests/assets/iris_model.onnx")

    onnx_model = add_intermediate_layers_as_outputs(
        onnx.load("tests/assets/iris_model.onnx")
    )

    # Create a dummy input
    dummy_input = np.random.randn(1, 2).astype(np.float32)
    print(f"Dummy input shape: {dummy_input.shape}")
    print(f"Dummy input: {dummy_input}")
    # Run the model through onnx inference session
    session = onnxruntime.InferenceSession(onnx_model.SerializeToString())
    input_name = session.get_inputs()[0].name
    onnx_outputs = session.run(None, {input_name: dummy_input})

    zerok_outputs = from_onnx(onnx_model, dummy_input)
    graph_output = np.sum(zerok_outputs[0])
    print(f"ONNX output: {onnx_outputs[0]}")

    print([dequantization(o.data) for o in zerok_outputs[0][0]])
    print(
        f"Graph output: {graph_output}, dequantized: {dequantization(graph_output.data)}"
    )

    start = time.time()
    layered_circuit, _, layers = Value.compile_layered_circuit(graph_output, True)
    print(f"Time to compile: {time.time() - start}")
    for i in range(100):
        print(f"Run {i}")
        start = time.time()
        prover = ZkProver(layered_circuit)
        assert prover.prove()
        print(f"Time to prove: {time.time() - start}")
        proof_transcript = prover.proof_transcript.to_bytes()
        print(f"Time to prove: {time.time() - start}")
        start = time.time()
        verifier = ZkVerifier(layered_circuit)
        verifier.run_verifier(proof_transcript=proof_transcript)
        print(f"Time to verify: {time.time() - start}")


if __name__ == "__main__":
    main()
