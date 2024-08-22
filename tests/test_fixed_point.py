from zkgraph.polynomials.field import (
    ModularInteger,
    quantization,
    dequantization,
    qlt,
    qgt,
    qle,
    qge,
)

signs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]


# testing multiplication, division, addition, exponentiation, and negation
def test_operations():
    for i in range(4):
        a_sign, b_sign = signs[i]
        a = 3.1 * a_sign
        b = 4.0 * b_sign
        aq = ModularInteger(a)
        bq = ModularInteger(b)
        c = aq + bq
        d = c * bq
        dd = d**2
        ed = dd / d
        e = ed**2
        assert dequantization(e) == (((a + b) * b) ** 2)
        assert dequantization(ModularInteger(1) / ModularInteger(2)) == 0.5
        assert -aq == ModularInteger(-a)


# test division
def test_division():
    a = ModularInteger(32)
    b = ModularInteger(2)
    for i in range(4):
        a_sign, b_sign = signs[i]
        a = 32 * a_sign
        b = 2 * b_sign
        aq = ModularInteger(a)
        bq = ModularInteger(b)
        c = aq / bq
        assert dequantization(c) == a / b


# test multiplication operation with integers
def test_multiplication():
    a = ModularInteger(32)
    b = ModularInteger(2)
    for i in range(4):
        a_sign, b_sign = signs[i]
        a = 32 * a_sign
        b = 2 * b_sign
        aq = ModularInteger(a)
        bq = ModularInteger(b)
        c = aq * bq
        assert dequantization(c) == a * b


# testing comparison
def test_comparison():
    for i in range(4):
        a_sign, b_sign = signs[i]
        aq = 3.14 * a_sign
        bq = 2.78 * b_sign
        a_quantized = quantization(aq)
        b_quantized = quantization(bq)
        assert qlt(a_quantized, b_quantized) == (aq < bq)
        assert qgt(a_quantized, b_quantized) == (aq > bq)
        assert qle(a_quantized, b_quantized) == (aq <= bq)
        assert qge(a_quantized, b_quantized) == (aq >= bq)
