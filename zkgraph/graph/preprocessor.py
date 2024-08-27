import math
from typing import List, Dict, Union, Type
from collections import defaultdict
from zkgraph.circuits.circuit import LayeredCircuit, Gate, GateType, Layer
from zkgraph.graph.base import BaseValue
import time


powers_of_2 = {
    1: 2,
    2: 4,
    3: 8,
    4: 16,
    5: 32,
    6: 64,
    7: 128,
    8: 256,
    9: 512,
    10: 1024,
    11: 2048,
    12: 4096,
    13: 8192,
    14: 16384,
    15: 32768,
    16: 65536,
    17: 131072,
    18: 262144,
    19: 524288,
    20: 1048576,
    21: 2097152,
    22: 4194304,
    23: 8388608,
    24: 16777216,
    25: 33554432,
    26: 67108864,
    27: 134217728,
    28: 268435456,
    29: 536870912,
    30: 1073741824,
    31: 2147483648,
}


TGRAPH = Union[Type["BaseValue"]]
TVALUE = Union[Type["BaseValue"]]


def _is_power_of_two(x: int):
    return x in powers_of_2.values() and x < powers_of_2[31]


def preprocess_circuit(
    output: "BaseValue",
    Graph: TGRAPH,
    Value: TVALUE,
):
    circuit_layers = output.get_layers()
    circuit = list(circuit_layers[:])
    used_nodes_ids = {}

    def process_immediate_node(
        node: "BaseValue",
        layer: List["BaseValue"],
        used_nodes_ids: Dict[int, "BaseValue"],
    ):
        node_layer_id = node.layer_id
        next_nodes = node.next
        for next_node in next_nodes:
            next_node_layer_id = next_node.layer_id
            is_immediate_layer_above = next_node_layer_id - node_layer_id == 1
            used_nodes_ids[next_node.id] = next_node
            if is_immediate_layer_above and next_node._op != "relay":
                next_node_children = next_node._prev
                next_node_children_ids = [
                    n.id for n in next_node_children if n is not None
                ]
                left_child_id = next_node_children_ids[0]
                right_child_id = (
                    next_node_children_ids[1] if len(next_node_children) > 1 else None
                )
                current_layer_node_ids = [n.id for n in layer]
                if left_child_id in current_layer_node_ids:
                    left_child_idx = current_layer_node_ids.index(left_child_id)
                    next_node.left_child_idx = left_child_idx
                if right_child_id in current_layer_node_ids:
                    right_child_idx = current_layer_node_ids.index(right_child_id)
                    next_node.right_child_idx = right_child_idx
            if len(next_node.next):
                process_immediate_node(next_node, layer, used_nodes_ids)

    counter = 0
    for idx, layer in enumerate(circuit):

        for node_idx, node in enumerate(layer):
            if node.new:
                continue
            node_layer_id = node.layer_id
            next_nodes = node.next
            for next_node in next_nodes:
                counter += 1
                next_node_layer_id = next_node.layer_id
                is_immediate_layer_above = next_node_layer_id - node_layer_id == 1
                used_nodes_ids[next_node.id] = next_node
                if is_immediate_layer_above and next_node._op != "relay":
                    next_node_children = next_node._prev
                    next_node_children_ids = [
                        n.id for n in next_node_children if n is not None
                    ]
                    left_child_id = next_node_children_ids[0]
                    right_child_id = (
                        next_node_children_ids[1]
                        if len(next_node_children) > 1
                        else None
                    )
                    current_layer_node_ids = [n.id for n in layer]
                    if left_child_id in current_layer_node_ids:
                        left_child_idx = current_layer_node_ids.index(left_child_id)
                        next_node.left_child_idx = left_child_idx
                    if right_child_id in current_layer_node_ids:
                        right_child_idx = current_layer_node_ids.index(right_child_id)
                        next_node.right_child_idx = right_child_idx
                    # used_nodes.append(next_node)

                elif not is_immediate_layer_above:
                    layer_diff = next_node_layer_id - node_layer_id
                    layer_to_insert = node_layer_id + 1
                    current_past_node = node
                    current_past_node_layer_idx = [
                        n.id for n in circuit[layer_to_insert - 1]
                    ].index(current_past_node.id)
                    while layer_diff > 1:
                        counter += 1
                        bottom_relay = Value(
                            node.data,
                            [current_past_node, None],
                            "relay",
                            integer=False,
                        )
                        bottom_relay.new = True
                        current_past_node.next.append(bottom_relay)
                        used_nodes_ids[bottom_relay.id] = bottom_relay
                        bottom_relay._prev = [current_past_node, None]
                        bottom_relay.layer_id = layer_to_insert
                        circuit[layer_to_insert].append(bottom_relay)
                        bottom_relay.left_child_idx = current_past_node_layer_idx
                        bottom_relay.right_child_idx = None
                        current_past_node = bottom_relay
                        layer_diff -= 1
                        layer_to_insert += 1
                        current_past_node_layer_idx = len(circuit[layer_to_insert]) - 1
                    node_idx_prev = [
                        n.id for n in next_node._prev if n is not None
                    ].index(node.id)
                    next_node._prev[node_idx_prev] = bottom_relay
                    next_node.left_child_idx = node_idx_prev
                    next_node.right_child_idx = None
                is_not_connected_to_root = not len(node._prev) and idx > 0
                if is_not_connected_to_root:
                    current_node_layer_id = node.layer_id
                    current_node = node
                    layer_to_insert = next_node_layer_id + 1
                    input_layer = 0
                    current_node_layer_diff = current_node_layer_id - input_layer
                    while current_node_layer_diff > 0:
                        counter += 1
                        bottom_relay = Value(
                            node.data,
                            integer=False,
                        )
                        bottom_relay.new = True
                        current_node._prev = [bottom_relay, None]
                        current_node._op = "relay"
                        bottom_relay.layer_id = current_node_layer_id - 1
                        bottom_relay.next.append(current_node)
                        circuit[current_node_layer_id - 1].append(bottom_relay)
                        current_node.left_child_idx = (
                            len(circuit[current_node_layer_id - 1]) - 1
                        )
                        current_node.right_child_idx = None
                        current_node_layer_diff -= 1
                        current_node_layer_id -= 1
                        used_nodes_ids[bottom_relay.id] = bottom_relay
                        current_node = bottom_relay
    return circuit


def to_circuit(
    output: "BaseValue",
    Graph: TGRAPH,
    Value: TVALUE,
):
    non_linearities: Dict[int, Dict[str, List[Value]]] = defaultdict(
        lambda: defaultdict(list)
    )
    start = time.time()
    connected_circuit_layers = list(reversed(preprocess_circuit(output, Graph, Value)))
    print("Time to preprocess circuit", time.time() - start)
    start = time.time()
    layers_len = len(connected_circuit_layers)
    range_len = range(layers_len)
    switch_map = {k: v for k, v in zip(reversed(range_len), range_len)}
    for layer in connected_circuit_layers:
        for node in layer:
            node.layer_id = switch_map[node.layer_id]
            for next_node in node.next:
                next_node.layer_id = switch_map[next_node.layer_id]
    print("Time to switch layers", time.time() - start)
    idx = len(connected_circuit_layers[:-1]) - 1
    start = time.time()
    # Add dummy gates to the last layer if the number of elements is not a power of 2
    num_elements_current_layer = len(connected_circuit_layers[0])
    layer = connected_circuit_layers[0]
    corrected_num_elements_current_layer = 0
    if not _is_power_of_two(num_elements_current_layer):
        for i in range(31):
            if num_elements_current_layer <= powers_of_2[i + 1]:
                corrected_num_elements_current_layer = powers_of_2[i + 1]
                break
        if corrected_num_elements_current_layer == 0:
            raise ValueError("Number of elements in the next layer is too large")
    remaining_elements_current_layer = (
        corrected_num_elements_current_layer - num_elements_current_layer
    )
    if remaining_elements_current_layer > 0:
        for i in range(remaining_elements_current_layer):
            new_node = Graph(
                0,
                [Value(0), None],
                "relay",
                dummy_gate=True,
            )
            new_node.layer_id = idx
            new_node.left_child_idx = num_elements_current_layer + i
            layer.append(new_node)
    for idx in range(1, len(connected_circuit_layers)):
        layer = connected_circuit_layers[idx]
        num_elements_last_layer = len(connected_circuit_layers[idx - 1])
        num_elements_current_layer = len(layer)
        max_elements = max(num_elements_current_layer, num_elements_last_layer)
        corrected_num_elements_current_layer = 0
        if not _is_power_of_two(max_elements):
            for i in range(31):
                if num_elements_current_layer > powers_of_2[i + 1]:
                    continue
                if num_elements_current_layer <= powers_of_2[i + 1]:
                    corrected_num_elements_current_layer = powers_of_2[i + 1]
                    break
            if corrected_num_elements_current_layer == 0:
                raise ValueError("Number of elements in the next layer is too large")
        else:
            corrected_num_elements_current_layer = max_elements
        remaining_elements_current_layer = (
            corrected_num_elements_current_layer - num_elements_current_layer
        )
        if remaining_elements_current_layer > 0:
            for i in range(remaining_elements_current_layer):
                new_node = Graph(
                    0,
                    [Value(0), None],
                    "relay",
                    dummy_gate=True,
                )
                new_node.layer_id = idx
                new_node.left_child_idx = num_elements_current_layer + i
                layer.append(new_node)
    print("Time to add dummy gates", time.time() - start)
    return connected_circuit_layers, non_linearities


def compile_layered_circuit(
    output: "BaseValue", Graph: TGRAPH, Value: TVALUE, integer=False, debug=False
):

    start = time.time()
    connected_circuit_layers, non_linearities = to_circuit(output, Graph, Value)
    print("Time to compile circuit relays", time.time() - start)
    start = time.time()
    circuit = LayeredCircuit()
    circuit.size = len(connected_circuit_layers)
    circuit.total_depth = len(connected_circuit_layers)
    circuit.circuit = []
    for idx, base_layer in enumerate(reversed(connected_circuit_layers)):
        layer_arr = []

        for node in base_layer:
            if idx == 0:
                layer_arr.append(
                    Gate(
                        GateType.Input,
                        0,
                        node.data if not integer else node.data_int,
                        0,
                        0,
                        False,
                    )
                )
            else:
                if len(node._prev) == 0:
                    continue
                if len(node._prev) <= 1:
                    raise ValueError("Node has only one child")
                right_child = node._prev[1]
                left_child_idx = node.left_child_idx
                right_child_idx = node.right_child_idx if right_child else 0
                gate_type = GateType.Mul
                if node._op == "relay":
                    gate_type = GateType.Relay
                    if left_child_idx is None:
                        if right_child_idx is None:
                            raise ValueError(
                                "Both left and right child indices are None"
                            )
                        left_child_idx = right_child_idx
                        right_child_idx = 0
                elif node._op == "+":
                    gate_type = GateType.Add
                if left_child_idx is None or right_child_idx is None:
                    raise ValueError(
                        f"Child indices are not defined for node at layer: {idx}"
                    )
                layer_arr.append(
                    Gate(
                        gate_type,
                        node.layer_id,
                        left_child_idx,
                        right_child_idx,
                        0,
                        False,
                    )
                )
        base_layer_len = len(base_layer)
        layer = Layer(gates=layer_arr[:])
        layer.bitLength = int(math.log2(base_layer_len)) if base_layer_len > 1 else 1
        layer.size = base_layer_len
        circuit.circuit.append(layer)
    print("Time to compile layered circuit", time.time() - start)
    if debug:
        return circuit, non_linearities, connected_circuit_layers
    return circuit, non_linearities
