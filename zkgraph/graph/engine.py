import math
from uuid import uuid4


from zkgraph.polynomials.field import (
    ModularInteger,
    qdiv,
    qexp,
    qmul,
    qadd,
)

from zkgraph.graph.preprocessor import (
    preprocess_circuit,
    compile_layered_circuit,
    to_circuit,
)
from zkgraph.graph.base import LayerList, BaseValue


def clear(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            LayerList.clear()

    return inner


class Value(BaseValue):
    """stores a single scalar value and its gradient"""

    def __init__(
        self,
        data,
        _children=(),
        _op="",
        nl_op="",
        dummy_gate=False,
        no_grad=False,
        integer=True,
        past_node_ids=[],
    ):
        self.data = data
        self.data_int = None
        self.grad = 0
        self.sign = None
        self.layer_id = None
        self.scaled = False
        self._prev = _children
        self._op = _op  # the op that produced this node, for graphviz / debugging / etc
        self.no_grad = no_grad
        self.nl_op = nl_op
        self.left_child_idx = None
        self.right_child_idx = None
        self.dummy_gate = dummy_gate
        self.id = uuid4().int
        self.integer = integer
        self.past_node_ids = past_node_ids
        self.next = []
        self.counter = 0
        self.new = False
        if self.integer and not len(_children):
            self.data = ModularInteger(self.data).val

    def compute_layer_id(self, left, right, output):
        left_layer_id = left.layer_id
        right_layer_id = right.layer_id
        if left_layer_id is not None and right_layer_id is None:
            right.layer_id = left_layer_id
        elif right_layer_id is not None and left_layer_id is None:
            left.layer_id = right_layer_id
        elif left_layer_id is None and right_layer_id is None:
            len_layers = 1 if len(LayerList) > 0 else 0
            left.layer_id = len_layers
            right.layer_id = len_layers
        left_layer_id = left.layer_id
        right_layer_id = right.layer_id
        next_layer_id = max(left_layer_id, right_layer_id) + 1
        output.layer_id = next_layer_id
        self.set_layer_element(left_layer_id, left)
        self.set_layer_element(right_layer_id, right)
        self.set_layer_element(next_layer_id, output)
        left_layer_idx = [n.id for n in LayerList[left_layer_id]]
        right_layer_idx = [n.id for n in LayerList[right_layer_id]]
        left_node_idx = left_layer_idx.index(left.id)
        right_node_idx = right_layer_idx.index(right.id)
        output.left_child_idx = left_node_idx
        output.right_child_idx = right_node_idx

    def get_layers(self):
        return LayerList

    def set_layer_element(self, layer_id, element):
        diff = (layer_id + 1) - len(LayerList)
        if diff > 0:
            for _ in range(diff):
                LayerList.append([])
        layer_ids = [n.id for n in LayerList[layer_id] if n.id == element.id]
        if len(layer_ids):
            return
        LayerList[layer_id].append(element)

    def delete_layer_element(self, layer_id, element):
        layer_ids = [n.id for n in LayerList[layer_id] if n.id == element.id]
        if len(layer_id):
            element_idx = layer_ids.index(element.id)
            LayerList[layer_id].remove(element_idx)
        else:
            raise ValueError("Element not found in layer")

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        result = qadd(self.data, other.data)
        out = Value(
            result,
            [self, other],
            "+",
            past_node_ids=self.past_node_ids,
        )
        self.compute_layer_id(self, other, out)
        other.next.append(out)
        self.next.append(out)

        return out

    def __mul__(self, other):
        # TODO: Add the features here for all methods.
        if other is None:
            raise ValueError("Other value is None")
        other = other if isinstance(other, Value) else Value(other)
        result = qmul(self.data, other.data)
        out = Value(
            result,
            [self, other],
            "*",
            past_node_ids=self.past_node_ids,
        )
        self.compute_layer_id(self, other, out)
        other.next.append(out)
        self.next.append(out)

        return out

    def __pow__(self, other):
        assert isinstance(
            other, (int, float)
        ), "only supporting int/float powers for now"
        t = qexp(self.data, other)
        result = qdiv(t, self.data)
        right: Value = Value(result, integer=False)
        # t = self.data**other
        # right: Value = Value(t / self.data)
        out = Value(t, [self, right], "*", nl_op="**", past_node_ids=self.past_node_ids)
        self.compute_layer_id(self, right, out)
        right.next.append(out)
        self.next.append(out)

        return out

    def tanh(self):
        x = self.data
        t = (math.exp(2 * x) - 1) / (math.exp(2 * x) + 1)
        if self.integer:
            t = round(t, 5)
        right: Value = t / self
        out = Value(
            t, [self, right], "*", nl_op="tanh", past_node_ids=self.past_node_ids
        )
        self.compute_layer_id(self, right, out)
        right.next.append(out)
        self.next.append(out)

        return out

    def exp(self):
        x = self.data
        if self.integer:
            t = round(math.exp(x), 5)
        else:
            t = math.exp(x)

        right: Value = t / self
        out = Value(
            t, [self, right], "*", nl_op="exp", past_node_ids=self.past_node_ids
        )
        self.compute_layer_id(self, right, out)
        self.next.append(out)
        right.next.append(out)

        return out

    def log(self):
        x = self.data
        if self.integer:
            t = round(math.log(x), 5)
        else:
            t = math.log(x)

        right: Value = t / self
        out = Value(
            t, [self, right], "*", nl_op="log", past_node_ids=self.past_node_ids
        )
        self.compute_layer_id(self, right, out)
        self.next.append(out)
        right.next.append(out)
        return out

    def relu(self):
        t = 0 if self.data < 0 else self.data
        right: Value = Value(qdiv(t, self.data), integer=False)
        out = Value(t, [self, right], "*", nl_op="ReLU")
        self.compute_layer_id(self, right, out)
        self.next.append(out)
        right.next.append(out)

        return out

    def __neg__(self):  # -self
        return self * -1

    def __radd__(self, other):  # other + self
        return self + other

    def __sub__(self, other):  # self - other
        return self + (-other)

    def __rsub__(self, other):  # other - self
        return other + (-self)

    def __rmul__(self, other):  # other * self
        return self * other

    def __truediv__(self, other):  # self / other
        return self * other**-1

    def __rtruediv__(self, other):  # other / self
        return other * self**-1

    def __repr__(self):
        return f"Value(data={self.data}, grad={self.grad})"

    @staticmethod
    def to_circuit(output: "Value", debug: bool = False):
        return to_circuit(output, Value, Value, debug=debug)

    @staticmethod
    @clear
    def compile_layered_circuit(output: "Value", debug: bool = False):
        return compile_layered_circuit(output, Value, Value, debug=debug)

    @staticmethod
    def proprocess_circuit(output: "Value", debug: bool = False):
        return preprocess_circuit(output, Value, Value)
