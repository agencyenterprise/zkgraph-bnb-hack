from py_ecc.optimized_bls12_381.optimized_curve import (
    G1,
    G2,
    multiply as ecc_multiply,
    add as ecc_add,
    is_on_curve,
    curve_order,
    FQ,
    FQ2,
    neg as ecc_negate,
)
from py_ecc.optimized_bls12_381.optimized_pairing import pairing

TG2P = tuple[FQ2, tuple[tuple[int]]]
TG1P = tuple[FQ, tuple[tuple[int]]]
TPP = tuple[TG2P, TG2P]
