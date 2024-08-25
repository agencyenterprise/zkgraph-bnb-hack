# The code below is based on the Libra implementation found at https://github.com/sunblaze-ucb/Libra


from typing import List
from zkgraph.polynomials.field import FiniteField, PRIME_MODULO
from zkgraph.types.gate import GateType

DOMAIN = FiniteField(PRIME_MODULO)


class Gate:
    def __init__(
        self, ty: GateType, l: int, u: int, v: int, c: FiniteField, is_assert_zero: bool
    ):
        """Initializes a new instance of the Gate class.

        Args:
            ty (GateType): The gate type
            l (int): index layer of the left side
            u (int): index of the left input layer at layer l
            v (int): index of the right input layer at layer l
            c (FiniteField): Element of a finite field
            is_assert_zero (bool): Whether the gate is an assertion gate
        """
        self.ty: GateType = ty
        self.l: int = l  # index layer of the left side
        self.u: int = u  # index of the left input layer at layer l
        self.v: int = v  # index of the right input layer at layer l
        self.lv: int = (
            0  # represent an alternative or secondary layer index for the second input v
        )
        self.c: FiniteField = c  # This should be an element of a finite field
        self.is_assert: bool = is_assert_zero


class Layer:
    def __init__(self, gates: List[Gate] = []):
        self.gates: List[Gate] = gates
        self.bitLength: int = 0
        self.size: int = 0
        self.dadId: List[List[int]] = []  # map from subset id to real id
        self.dadBitLength: List[int] = []  # subset bit length
        self.dadSize: List[int] = []  # subset size
        self.maxDadSize: int = 0  # max subset size
        self.maxDadBitLength: int = 0  # max subset bit length


class LayeredCircuit:
    def __init__(self, domain: FiniteField = DOMAIN):
        self.circuit: List[Layer] = []
        self.size: int = 0
        self.domain = domain
        self.zero = domain.zero
        self.total_depth = 0
        self.prime = domain.characteristic()
