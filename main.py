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
import subprocess


use_mkzg = int(os.environ.get("USE_PCS", 0))
use_noir = int(os.environ.get("USE_NOIR", 0))


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
    layered_circuit, _ = Value.compile_layered_circuit(graph_output)
    for _ in range(1000):

        start = time.time()
        if use_mkzg:
            public_parameters = {
                "r_pp": "./tests/assets/random_polynomial_r_powers_of_tau.ptau",
                "zk_pp": "./tests/assets/zk_sumcheck_powers_of_tau.ptau",
            }
            prover = ZkProver(
                layered_circuit, mkzg=use_mkzg, public_parameters=public_parameters
            )
            verifier = ZkVerifier(
                layered_circuit, mkzg=True, public_parameters=public_parameters
            )
        else:
            prover = ZkProver(layered_circuit, mkzg=False)
            verifier = ZkVerifier(layered_circuit, mkzg=False)
        assert prover.prove()
        print(f"Time to prove: {time.time() - start}")
        proof_transcript = prover.proof_transcript.to_bytes()
        print(f"Time to prove: {time.time() - start}")
        start = time.time()
        verifier.run_verifier(proof_transcript=proof_transcript)
        print(f"Time to verify: {time.time() - start}")
        if use_noir:
            verifier.get_noir_transcript()
            subprocess.call(
                "cd onchain_verifier/ && nargo execute iris && bb prove -b ./target/onchain_verifier.json -w ./target/iris.gz -o ./target/proof && bb write_vk -b target/onchain_verifier.json -o ./target/vk && bb verify -k ./target/vk -p ./target/proof && bb contract",
                shell=True,
            )


if __name__ == "__main__":
    main()
