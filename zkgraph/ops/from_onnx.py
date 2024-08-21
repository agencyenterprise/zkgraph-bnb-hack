# import pdb
import onnx
import numpy as np

from zkgraph.graph.engine import Value
from zkgraph.ops import elementwise, gemm, conv

onnx_to_op = {"Gemm": gemm.Gemm, "Relu": elementwise.ElementWise, "Conv": conv.Conv}


def from_onnx(onnx_model, input_data):

    calculated_values = {}

    for initializer in onnx_model.graph.initializer:
        tensor = onnx.numpy_helper.to_array(initializer)
        calculated_values[initializer.name] = np.vectorize(Value)(tensor)

    # store input value
    input_name = onnx_model.graph.input[0].name
    calculated_values[input_name] = np.vectorize(Value)(input_data)

    for node in onnx_model.graph.node:
        # print(node.name)
        node_input_values = [calculated_values[input_name] for input_name in node.input]

        # select the right class for this node
        op_class = onnx_to_op[node.op_type]

        # initialize this class
        op = op_class.from_onnx(node)

        # pdb.set_trace()
        # apply the operation
        node_value = op(*node_input_values)

        # save the value at this node
        calculated_values[node.output[0]] = node_value

    return [calculated_values[output.name] for output in onnx_model.graph.output]
