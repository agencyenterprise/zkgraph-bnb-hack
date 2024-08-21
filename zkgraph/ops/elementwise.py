from typing import Callable

import numpy as np

from onnx import NodeProto


class ElementWise:
    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, x):
        return np.vectorize(self.func)(x)

    @classmethod
    def from_onnx(cls, onnx_node: NodeProto):

        if onnx_node.op_type == "Relu":

            func = lambda x: x.relu()

        return cls(func)
