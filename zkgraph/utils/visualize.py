from graphviz import Digraph


def trace(root):
    # builds a set of all nodes and edges in a graph
    nodes, edges = [], []
    visited = []

    def build(v):
        if v is not None and v.id not in visited:
            nodes.append(v)
            visited.append(v.id)
            for child in v._prev:
                if child is not None:
                    edges.append((child, v))
                    build(child)

    build(root)
    return nodes, edges


def draw_dot(root):
    dot = Digraph(format="svg", graph_attr={"rankdir": "LR"})  # LR = left to right

    nodes, edges = trace(root)
    for n in nodes:
        uid = str(n.id)
        # for any value in the graph, create a rectangular ('record') node for it
        dot.node(
            name=uid,
            label="{ data %.4f layer %.4f }" % (n.data, n.layer_id),
            shape="record",
        )
        if n._op:
            # if this value is a result of some operation, create an op node for it
            dot.node(name=uid + n._op, label=n._op)
            # and connect this node to it
            dot.edge(uid + n._op, uid)

    for n1, n2 in edges:
        # connect n1 to the op node of n2
        dot.edge(str(n1.id), str(n2.id) + n2._op)

    return dot
