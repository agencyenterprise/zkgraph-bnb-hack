from zkgraph.graph.engine import Value
from zkgraph.prover.prover import ZkProver
from zkgraph.utils.visualize import draw_dot
import numpy as np


def test_circuit_generation_value_scalars():
    A = Value(-1)
    B = Value(2)
    C = A + B
    for i in range(1, 3):
        one = Value(i)
        C = C * one
    circuit, _, layers = Value.compile_layered_circuit(C, True)
    draw_dot(layers[0][0]).render("tests/assets/scalars", format="png", cleanup=True)
    assert ZkProver(circuit).prove()


def test_circuit_generation_matrix_multiplication():
    A = np.array([[Value(1), Value(2)], [Value(2), Value(1)]])
    B = np.array([Value(3), Value(4)])
    C = A @ B
    circuit, _ = Value.compile_layered_circuit(C[0])
    draw_dot(C[0]).render(
        "tests/assets/matrix_multiplication", format="png", cleanup=True
    )
    assert circuit.size == 4
    assert ZkProver(circuit).prove()


import numpy as np
import onnx
import onnxruntime
import os
from zkgraph.graph.engine import Value
from zkgraph.ops.onnx_utils import generate_small_iris_onnx_model
from zkgraph.ops.from_onnx import from_onnx
from zkgraph.prover.prover import ZkProver


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


def test_from_onnx_gemm_and_relu():

    if "iris_model.onnx" not in os.listdir("tests/assets/"):
        generate_small_iris_onnx_model(onnx_output_path="tests/assets/iris_model.onnx")

    onnx_model = add_intermediate_layers_as_outputs(
        onnx.load("tests/assets/iris_model.onnx")
    )

    # Create a dummy input
    dummy_input = np.random.randn(1, 2).astype(np.float32)

    # Run the model through onnx inference session
    session = onnxruntime.InferenceSession(onnx_model.SerializeToString())
    input_name = session.get_inputs()[0].name
    onnx_outputs = session.run(None, {input_name: dummy_input})

    zerok_outputs = from_onnx(onnx_model, dummy_input)

    graph_output = np.sum(zerok_outputs[0])
    layered_circuit, _ = Value.compile_layered_circuit(graph_output)
    assert ZkProver(layered_circuit).prove()
