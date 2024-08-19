# import random
# from typing import List
from onnx import NodeProto

from zkgraph.graph.engine import Value
from zkgraph.ops.onnx_utils import get_proto_attribute_value
import numpy as np


# defines gemm: "general matrix muliply"
# see e.g. https://en.wikipedia.org/wiki/Basic_Linear_Algebra_Subprograms#Level_3
#      and https://github.com/onnx/onnx/blob/c7717bb39c684a6d86c82a5bb1d4c0e5d90353fe/onnx/reference/ops/op_gemm.py


class Gemm:
    def __init__(
        self,
        a=None,
        b=None,
        c=None,
        alpha=1,
        beta=None,
        transA=None,
        transB=False,
        **kwargs
    ):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.transA = transA
        self.transB = transB

    def __call__(
        self, a=None, b=None, c=None, alpha=None, beta=None, transA=None, transB=None
    ):
        # need to play these games because of 'mutable defaults' problem
        a = a if a is not None else self.a
        b = b if b is not None else self.b
        c = c if c is not None else self.c
        alpha = alpha if alpha is not None else self.alpha
        beta = beta if beta is not None else self.beta
        transA = transA if transA is not None else self.transA
        transB = transB if transB is not None else self.transB

        if transA:
            a = a.T
        if transB:
            b = b.T

        o = np.dot(a, b) * alpha
        if c is not None and beta != 0:
            o += c * beta
        return o

    @classmethod
    def from_onnx(cls, onnx_node: NodeProto):
        return cls(
            **{a.name: get_proto_attribute_value(a) for a in onnx_node.attribute}
        )
