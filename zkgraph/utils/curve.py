# Some methods are taken from https://github.com/HarryR/ethsnarks
from py_ecc.fields.field_elements import FQ as Field
import py_ecc.bn128 as b
from collections import defaultdict
from typing import NewType

PRIMITIVE_ROOT = 5
G1Point = NewType("G1Point", tuple[b.FQ, b.FQ])
G2Point = NewType("G2Point", tuple[b.FQ2, b.FQ2])


class Scalar(Field):
    _COUNTS = None
    field_modulus = b.curve_order

    def __hash__(self):
        return hash((self.n, self.field_modulus))

    @classmethod
    def _disable_counting(cls):
        cls._COUNTS = None

    @classmethod
    def _print_counts(cls):
        if cls._COUNTS is not None:
            for k in sorted(cls._COUNTS.keys()):
                print(k, "=", cls._COUNTS[k])
            print()

    @classmethod
    def _count(cls, what):
        if cls._COUNTS is not None:
            cls._COUNTS[what] += 1

    @classmethod
    def _reset_counts(cls):
        cls._COUNTS = defaultdict(int)

    # Gets the first root of unity of a given group order
    @classmethod
    def root_of_unity(cls, group_order: int):
        assert (cls.field_modulus - 1) % group_order == 0
        return Scalar(PRIMITIVE_ROOT) ** ((cls.field_modulus - 1) // group_order)

    # Gets the full list of roots of unity of a given group order
    @classmethod
    def roots_of_unity(cls, group_order: int):
        o = [Scalar(1), cls.root_of_unity(group_order)]
        while len(o) < group_order:
            o.append(o[-1] * o[1])
        return o

    def _other_n(self, other):
        if isinstance(other, Scalar):
            if other.field_modulus != self.field_modulus:
                raise RuntimeError("Other field element has different modulus")
            return other.n
        if not isinstance(other, int):
            raise RuntimeError("Not a valid value type: " + str(type(other).__name__))
        return other

    def exp(self, e):
        e = self._other_n(e)
        self._count('exp')
        return Scalar(pow(self.n, e, self.field_modulus))

    def __pow__(self, e):
        return self.exp(e)

Base = NewType("Base", b.FQ)

def ec_mul(pt, coeff):
    if hasattr(coeff, "n"):
        coeff = coeff.n
    return b.multiply(pt, coeff % b.curve_order)


def ec_lincomb(pairs):
    o = b.Z1
    for pt, coeff in pairs:
        o = b.add(o, ec_mul(pt, coeff))
    return o
