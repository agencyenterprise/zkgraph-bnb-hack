from collections import defaultdict
import dill
from abc import ABC, abstractmethod
from typing import Optional
from zkgraph.polynomials.poly import QuadraticPoly, QuintuplePoly
from zkgraph.polynomials.field import FiniteField, PRIME_MODULO as curve_order


class Proof(ABC):
    def __init__(self, keys: list[bytes] = []):
        self.keys = keys
        self.proof = defaultdict(list)

    @abstractmethod
    def retrieve_transcript_by_label(self, label: bytes):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def flatten(self):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def to_bytes(self):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def from_bytes(self, data):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def to_file(self, path):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def from_file(self, path):
        raise NotImplementedError("Method not implemented")


class ZeroKProofTranscript(Proof):
    def __init__(self):
        keys = [
            b"phase_1",
            b"alpha_beta_sum",
            b"phase_2",
            b"v_u",
            b"v_v",
            b"final_gkr_round",
            b"input",
            b"r_0",
            b"r_1",
            b"r_u",
            b"r_v",
            b"alpha",
            b"beta",
            b"rho",
            b"direct_relay_value",
            b"r_c",
            b"v_u_direct_relay",
        ]
        super().__init__(keys)
        self.label_counter = {key: 0 for key in keys}

    def retrieve_transcript_by_label(self, label: bytes, idx: Optional[int] = None):
        domain = FiniteField(curve_order)
        if label not in self.keys:
            raise ValueError(f"Label {label} not found in proof transcript")
        if idx is not None:
            if idx >= len(self.proof[label]):
                raise ValueError(f"Index {idx} out of bounds for label {label}")
            self.label_counter[label] = idx + 1
            return domain(self.proof[label][idx], False)

        last_idx = self.label_counter[label]
        if last_idx >= len(self.proof[label]):
            raise ValueError(f"Index {idx} out of bounds for label {label}")
        value = self.proof[label][last_idx]

        self.label_counter[label] += 1
        if label == b"phase_1" or label == b"phase_2" or label == b"final_gkr_round":
            coefficients = [domain(x, False) for x in dill.loads(value)]
            if not isinstance(coefficients, list):
                raise ValueError(f"Expected list for label {label}")

            if len(coefficients) == 6:
                return QuintuplePoly(domain, *coefficients)
            elif len(coefficients) == 3:
                return QuadraticPoly(domain, *coefficients)
            raise ValueError(
                f"Invalid number of coefficients for label {label}, must be 3 or 6"
            )

        return domain(dill.loads(value), False)

    def flatten(self):
        return self.proof

    def to_bytes(self):
        return dill.dumps(self.proof)

    def from_bytes(self, data):
        self.proof = dill.loads(data)

    def to_file(self, path):
        dill.dump(self.to_bytes(), open(path, "wb"))

    def from_file(self, path):
        dill.loads(dill.load(open(path, "rb")))
