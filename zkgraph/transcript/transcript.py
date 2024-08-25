# Code extracted from the https://github.com/NOOMA-42/pylookup/tree/main/src/plookup repository

from py_ecc.secp256k1.secp256k1 import bytes_to_int
from zkgraph.utils.curve import Scalar, G1Point
from zkgraph.transcript.merlin.merlin_transcript import MerlinTranscript
from zkgraph.polynomials.field import (
    FiniteField,
    ModularInteger,
    PRIME_MODULO as curve_order,
)
from zkgraph.polynomials.field import float_to_mod_float
from typing import Optional
import dill
from zkgraph.types.proof import Proof


class CommonTranscript(MerlinTranscript):
    def __init__(self, label: bytes, proof: Optional[Proof] = None) -> None:
        super().__init__(label)
        self.proof_transcript = proof

    def has_label(self, label: bytes) -> bool:
        if self.proof_transcript is None:
            return False
        if label not in self.proof_transcript.keys:
            raise ValueError(f"Label {label} not found in proof transcript")
        return True

    def append(self, label: bytes, item: bytes) -> None:
        self.append_message(label, item)

    def append_scalar(self, label: bytes, item: Scalar):
        value = item.n.to_bytes(32, "big")
        if self.has_label(label):
            self.proof_transcript.proof[label].append(dill.dumps(item.n))
        self.append_message(label, value)

    def append_sympy_ff(self, label: bytes, item: ModularInteger):
        value = item.val
        if self.has_label(label):
            self.proof_transcript.proof[label].append(dill.dumps(value))
        value = value.to_bytes(32, "big")
        self.append_message(label, value)

    def append_scalar_list(self, label: bytes, items: list[Scalar]):
        for item in items:
            self.append_scalar(label, item)

    def append_sympy_ff_list(self, label: bytes, items: list[ModularInteger]):
        values = [item.val for item in items]
        if self.has_label(label):
            self.proof_transcript.proof[label].append(dill.dumps(values))
        for value in values:
            value = value.to_bytes(32, "big")
            self.append_message(label, value)

    def append_point(self, label: bytes, item: G1Point):
        if self.has_label(label):
            self.proof_transcript.proof[label].append(
                dill.dumps([item[0].n, item[1].n])
            )
        self.append_message(label, item[0].n.to_bytes(32, "big"))
        self.append_message(label, item[1].n.to_bytes(32, "big"))

    def get_and_append_challenge(self, label: bytes) -> Scalar:
        while True:
            challenge_bytes = self.challenge_bytes(label, 255)
            # @TODO: rewrite fixed point code to deal with higher precision
            f = Scalar(float_to_mod_float(bytes_to_int(challenge_bytes)))
            if f != Scalar.zero():  # Enforce challenge != 0
                self.append_scalar(label, f)
                return f

    def get_and_append_point(self, label: bytes, order: int) -> Scalar:
        while True:
            challenge_bytes = self.challenge_bytes(label, 255)
            f = Scalar(bytes_to_int(challenge_bytes))
            if f**order != Scalar.one():  # Enforce point not a root of unity
                self.append_scalar(label, f)
                return f

    def get_scalar_challenges(self, label: bytes, n: int) -> list[Scalar]:
        return [self.get_and_append_challenge(label) for _ in range(n)]

    def get_sympy_ff_challenges(self, label: bytes, n: int) -> list[ModularInteger]:
        domain = FiniteField(curve_order)
        return [domain(self.get_and_append_challenge(label).n, False) for _ in range(n)]
