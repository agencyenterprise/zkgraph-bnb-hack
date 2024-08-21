from typing import List, Iterator, Union

from zkgraph.polynomials.poly import (
    LinearPoly,
    QuadraticPoly,
)
from zkgraph.polynomials.field import FiniteField, ModularInteger


def my_resize(
    vec: List[ModularInteger], sz: int, domain: FiniteField
) -> List[ModularInteger]:
    return vec + [domain(0)] * (sz - len(vec)) if len(vec) < sz else vec


def my_resize_pol(
    vec: List[ModularInteger], sz: int, polynom: Union[LinearPoly, QuadraticPoly]
) -> List[ModularInteger]:
    return vec + [polynom] * (sz - len(vec)) if len(vec) < sz else vec


def init_half_table(
    beta_f: List[ModularInteger],
    beta_s: List[ModularInteger],
    r: Iterator[ModularInteger],
    init: ModularInteger,
    first_half: int,
    second_half: int,
    domain: FiniteField,
) -> tuple[List[ModularInteger], List[ModularInteger]]:
    beta_f[0] = init
    beta_s[0] = domain(1)

    for i in range(first_half):
        for j in range(1 << i):
            tmp = beta_f[j] * r[i]
            beta_f[j | (1 << i)] = tmp
            beta_f[j] = beta_f[j] - tmp

    for i in range(second_half):
        for j in range(1 << i):
            tmp = beta_s[j] * r[i + first_half]
            beta_s[j | (1 << i)] = tmp
            beta_s[j] = beta_s[j] - tmp
    return beta_f, beta_s


def init_beta_table_base(
    beta_g: List[ModularInteger],
    g_length: int,
    r: Iterator[ModularInteger],
    init: ModularInteger,
    domain: FiniteField,
) -> List[ModularInteger]:
    if g_length == -1:
        return beta_g
    assert len(beta_g) >= 1 << g_length, "beta_g should be at least 2^g_length in size"
    first_half = g_length >> 1
    second_half = g_length - first_half
    beta_f: List[ModularInteger] = [domain(0)] * (1 << first_half)
    beta_s: List[ModularInteger] = [domain(0)] * (1 << second_half)
    mask_fhalf = (1 << first_half) - 1
    if init != domain(0):
        beta_f, beta_s = init_half_table(
            beta_f, beta_s, r, init, first_half, second_half, domain
        )
        for i in range(1 << g_length):
            beta_g[i] = beta_f[i & mask_fhalf] * beta_s[i >> first_half]
    else:
        for i in range(1 << g_length):
            beta_g[i] = domain(0)
    return beta_g


def init_beta_table_alpha(
    beta_g: List[ModularInteger],
    g_length: int,
    r_0: Iterator[ModularInteger],
    r_1: Iterator[ModularInteger],
    alpha: ModularInteger,
    beta: ModularInteger,
    domain: FiniteField,
) -> List[ModularInteger]:
    first_half = g_length >> 1
    second_half = g_length - first_half
    beta_f: List[ModularInteger] = [domain(0)] * (1 << first_half)
    beta_s: List[ModularInteger] = [domain(0)] * (1 << second_half)
    mask_fhalf = (1 << first_half) - 1
    assert len(beta_g) >= 1 << g_length, "beta_g should be at least 2^g_length in size"
    if beta != domain(0):
        beta_f, beta_s = init_half_table(
            beta_f, beta_s, r_1, beta, first_half, second_half, domain
        )
        for i in range(1 << g_length):
            beta_g[i] = beta_f[i & mask_fhalf] * beta_s[i >> first_half]
    else:
        for i in range(1 << g_length):
            beta_g[i] = domain(0)

    if alpha == domain(0):
        return beta_g
    beta_f, beta_s = init_half_table(
        beta_f, beta_s, r_0, alpha, first_half, second_half, domain
    )
    for i in range(1 << g_length):
        beta_g[i] += beta_f[i & mask_fhalf] * beta_s[i >> first_half]
    return beta_g


def init_beta_table(
    beta_g: List[ModularInteger],
    g_length: int,
    r_0: Iterator[ModularInteger],
    r_1: Iterator[ModularInteger],
    domain: FiniteField,
    alpha: ModularInteger = None,
    beta: ModularInteger = None,
) -> List[ModularInteger]:
    if alpha is None and beta is None:
        return init_beta_table_base(beta_g, g_length, r_0, r_1, domain)
    return init_beta_table_alpha(beta_g, g_length, r_0, r_1, alpha, beta, domain)
